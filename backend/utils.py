import sys
import os
from pathlib import Path


def get_app_data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    data_dir = base / "BookBook"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_path() -> Path | None:
    """按优先级查找 config.json：
    1. 打包后（sys.frozen）：exe 同级目录（Tauri bundle.resources 会把 config.json 放在这里）
    2. 应用数据目录 %APPDATA%/BookBook
    3. 开发模式：项目根目录（backend/ 的上一级）
    """
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "config.json")
    candidates.append(get_app_data_dir() / "config.json")
    candidates.append(Path(__file__).resolve().parent.parent / "config.json")
    for c in candidates:
        if c.exists():
            return c
    return None


def load_app_config() -> dict:
    import json

    path = get_config_path()
    if path is None:
        print("[CONFIG] config.json not found in any candidate location, using defaults")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        print(f"[CONFIG] config.json loaded from {path}")
        return cfg
    except Exception as e:
        print(f"[CONFIG] Failed to load {path}: {e}, using defaults")
        return {}


def setup_debug_logging() -> Path:
    """打包（frozen/noconsole）模式：stdout/stderr 重定向到日志文件（否则为 None 会崩溃）。
    开发模式：保留控制台输出，否则报错全被吞进日志文件，终端一片空白。"""
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "backend_debug.log"
    if getattr(sys, "frozen", False) or sys.stdout is None or sys.stderr is None:
        try:
            f = open(str(log_file), "a", encoding="utf-8", buffering=1)
            sys.stdout = f
            sys.stderr = f
        except Exception:
            pass
    return log_file
