import sys
import asyncio
import json
from pathlib import Path

# --- PyInstaller --noconsole 加固 ---
# windowed 模式下 sys.stdout/stderr 为 None，
# 任何 print / uvicorn 日志写入都会导致进程崩溃。
# frozen 时把输出重定向到 exe 同级目录的 backend.log。
if getattr(sys, "frozen", False):
    _log_file = Path(sys.executable).parent / "backend.log"
    try:
        _log_stream = open(_log_file, "a", encoding="utf-8", buffering=1)
    except OSError:
        import os
        _log_stream = open(os.devnull, "w", encoding="utf-8")
    if sys.stdout is None:
        sys.stdout = _log_stream
    if sys.stderr is None:
        sys.stderr = _log_stream

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import books, generate, p2p
from routers import providers
from routers.p2p import p2p_service
from services.identity import generate_user_id

def get_project_root():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

_project_root = get_project_root()
_config_path = _project_root / "config.json"
if _config_path.exists():
    with open(_config_path, "r", encoding="utf-8") as f:
        _config = json.load(f)
else:
    _config = {}

BACKEND_PORT = int(_config.get("backend_port", 18140))
FRONTEND_PORT = int(_config.get("frontend_port", 5173))
P2P_PORT = int(_config.get("p2p_port", 47833))

app = FastAPI(title="AI eBook Generator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    init_db()
    # 启动 P2P TCP 服务器（后台运行）
    try:
        asyncio.create_task(p2p_service.start())
        print(f"[P2P] TCP server started on port {P2P_PORT}")
    except Exception as e:
        print(f"[P2P] Failed to start TCP server: {e}")


@app.on_event("shutdown")
async def shutdown():
    await p2p_service.stop()


@app.get("/api/identity")
def get_identity():
    return {"user_id": generate_user_id()}


@app.get("/api/active-model")
def get_active_model():
    from services.llm_service import get_active_provider_info

    info = get_active_provider_info()
    return info or {"active": None}


@app.get("/api/config")
def get_app_config():
    return {
        "backend_port": BACKEND_PORT,
        "frontend_port": FRONTEND_PORT,
        "p2p_port": P2P_PORT,
    }


app.include_router(books.router)
app.include_router(generate.router)
app.include_router(p2p.router)
app.include_router(providers.router)

if __name__ == "__main__":
    import uvicorn

    # 127.0.0.1 即可（仅供本机 Tauri 前端访问），避免防火墙弹窗；
    # frozen 模式下关闭 uvicorn 默认日志配置，防止它向已失效的终端流写日志
    _kwargs = {}
    if getattr(sys, "frozen", False):
        _kwargs["log_config"] = None  # 禁用 uvicorn 默认日志配置，防止写入失效的终端流
    uvicorn.run(app, host="127.0.0.1", port=BACKEND_PORT, **_kwargs)
