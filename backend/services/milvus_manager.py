"""用 Docker 以「sidecar 式」管理本机 Milvus standalone 容器。

背景：Milvus Lite 没有 Windows wheel，Windows 上要用向量索引只能跑 Docker 服务版。
本模块在后端（它本身就是 Tauri 的 sidecar 进程）启动时自动拉起 `milvus-standalone` 容器，
让 Milvus 的生命周期跟随 App —— 等价于"sidecar 式"管理。任何不可用情况（未装 Docker、
拉起失败）都安全返回，rag_service 会自动回落 SQLite/BM25。

等价于官方 `standalone_embed.bat start` 的逻辑：检测 docker → 容器在跑则跳过 → 存在则
docker start → 否则写 etcd 配置并 docker run → 轮询健康状态直至 healthy。
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path

from config import (
    MILVUS_URI,
    MILVUS_AUTOSTART,
    MILVUS_IMAGE,
    MILVUS_CONTAINER,
)
from utils import get_app_data_dir

# Windows 上隐藏子进程黑框
_CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

_EMBED_ETCD_YAML = (
    "listen-client-urls: http://0.0.0.0:2379\n"
    "advertise-client-urls: http://0.0.0.0:2379\n"
    "quota-backend-bytes: 4294967296\n"
    "auto-compaction-mode: revision\n"
    "auto-compaction-retention: '1000'\n"
)
_USER_YAML = "# Extra config to override default milvus.yaml\n"


def _run(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess | None:
    """跑一条 docker 命令；docker 不存在或异常返回 None。"""
    try:
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=_CREATE_NO_WINDOW,
        )
    except (FileNotFoundError, subprocess.SubprocessError, OSError) as e:
        print(f"[Milvus] command failed {args[:2]}: {e}")
        return None


def docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    r = _run(["docker", "version", "--format", "{{.Server.Version}}"], timeout=15)
    return bool(r and r.returncode == 0 and r.stdout.strip())


def _manages_local() -> bool:
    """仅当开启 autostart 且 MILVUS_URI 指向本机 http 服务时，才由本模块管理 Docker。"""
    if not MILVUS_AUTOSTART:
        return False
    uri = (MILVUS_URI or "").lower()
    if not uri.startswith("http"):
        return False  # Lite 本地文件模式，不需要 Docker
    return "127.0.0.1" in uri or "localhost" in uri


def _container_state() -> str | None:
    """返回容器状态字符串（running/exited/...）；不存在返回 None。"""
    r = _run(["docker", "inspect", "-f", "{{.State.Status}}", MILVUS_CONTAINER], timeout=15)
    if r and r.returncode == 0:
        return r.stdout.strip()
    return None


def _health() -> str | None:
    r = _run(["docker", "inspect", "-f", "{{.State.Health.Status}}", MILVUS_CONTAINER], timeout=15)
    if r and r.returncode == 0:
        return r.stdout.strip()
    return None


def is_ready() -> bool:
    """容器在跑且（无健康检查或）健康。"""
    if _container_state() != "running":
        return False
    h = _health()
    return h in (None, "", "healthy", "<no value>")


def _docker_run_args(data_dir: Path) -> list[str]:
    vol = data_dir / "volumes" / "milvus"
    embed_yaml = data_dir / "embedEtcd.yaml"
    user_yaml = data_dir / "user.yaml"
    vol.mkdir(parents=True, exist_ok=True)
    embed_yaml.write_text(_EMBED_ETCD_YAML, encoding="utf-8")
    user_yaml.write_text(_USER_YAML, encoding="utf-8")
    return [
        "docker", "run", "-d",
        "--name", MILVUS_CONTAINER,
        "--security-opt", "seccomp:unconfined",
        "-e", "ETCD_USE_EMBED=true",
        "-e", "ETCD_DATA_DIR=/var/lib/milvus/etcd",
        "-e", "ETCD_CONFIG_PATH=/milvus/configs/embedEtcd.yaml",
        "-e", "COMMON_STORAGETYPE=local",
        "-e", "DEPLOY_MODE=STANDALONE",
        "-v", f"{vol}:/var/lib/milvus",
        "-v", f"{embed_yaml}:/milvus/configs/embedEtcd.yaml",
        "-v", f"{user_yaml}:/milvus/configs/user.yaml",
        "-p", "19530:19530",
        "-p", "9091:9091",
        "-p", "2379:2379",
        "--health-cmd", "curl -f http://localhost:9091/healthz",
        "--health-interval", "30s",
        "--health-start-period", "90s",
        "--health-timeout", "20s",
        "--health-retries", "3",
        MILVUS_IMAGE,
        "milvus", "run", "standalone",
    ]


def ensure_started(timeout: int = 180) -> bool:
    """确保本机 Milvus 容器在运行。返回是否就绪。失败安全返回 False（调用方降级）。"""
    if not _manages_local():
        return False
    if not docker_available():
        print("[Milvus] Docker 不可用，跳过自动拉起（将回落 SQLite/BM25）")
        return False

    state = _container_state()
    if state == "running":
        ok = is_ready()
        if not ok:
            _wait_ready(timeout)
        return is_ready()

    if state is not None:
        # 容器已存在但停了
        print(f"[Milvus] starting existing container {MILVUS_CONTAINER}")
        _run(["docker", "start", MILVUS_CONTAINER], timeout=30)
    else:
        # 全新拉起（首次会拉镜像，可能较慢）
        print(f"[Milvus] creating container from {MILVUS_IMAGE} ...")
        data_dir = get_app_data_dir() / "milvus"
        data_dir.mkdir(parents=True, exist_ok=True)
        r = _run(_docker_run_args(data_dir), timeout=max(timeout, 300))
        if not (r and r.returncode == 0):
            print(f"[Milvus] docker run failed: {r.stderr if r else 'no docker'}")
            return False

    return _wait_ready(timeout)


def _wait_ready(timeout: int) -> bool:
    print("[Milvus] waiting for container to become healthy ...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_ready():
            print("[Milvus] ready.")
            return True
        time.sleep(2)
    print("[Milvus] not ready within timeout; will fallback for now (may recover later).")
    return False


def stop() -> None:
    """停止容器（可选；默认不在退出时调用，留着下次更快启动）。"""
    if _manages_local() and docker_available():
        _run(["docker", "stop", MILVUS_CONTAINER], timeout=30)
