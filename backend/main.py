import sys
import asyncio
import json
from pathlib import Path
from utils import get_app_data_dir, setup_debug_logging, load_app_config

log_file = setup_debug_logging()
print(f"[BOOT] Backend starting, sys.platform={sys.platform}, sys.frozen={getattr(sys, 'frozen', False)}")
print(f"[BOOT] sys.executable={sys.executable}")
print(f"[BOOT] APPDATA={__import__('os').environ.get('APPDATA', 'NOT SET')}")
print(f"[BOOT] DATA_DIR={get_app_data_dir()}")
print(f"[BOOT] Log file={log_file}")

import os
import threading


def _watch_parent_exit():
    """Tauri sidecar 模式下父进程退出会关闭 stdin 管道。
    读到 EOF 立即自杀，即使主程序崩溃/被强杀也不会留下僵尸后端占用端口。"""
    try:
        if sys.stdin is None:
            return
        sys.stdin.buffer.read()  # 阻塞直到父进程关闭管道
    except Exception:
        pass
    print("[BOOT] Parent process gone, shutting down backend")
    os._exit(0)


if getattr(sys, "frozen", False):
    threading.Thread(target=_watch_parent_exit, daemon=True).start()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import books, generate, p2p
from routers import providers
from routers import knowledge
from routers import settings as settings_router
from routers.p2p import p2p_service
from services.identity import generate_user_id

_config = load_app_config()

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
    try:
        init_db()
        print("[DB] init_db() OK - tables created")
    except Exception as e:
        print(f"[DB] init_db() FAILED: {e}")
        import traceback
        traceback.print_exc()
    # 自动用 Docker 以 sidecar 式拉起本机 Milvus（后台线程，不阻塞启动；失败则回落 SQLite/BM25）
    try:
        from config import MILVUS_AUTOSTART
        if MILVUS_AUTOSTART:
            import threading
            from services.milvus_manager import ensure_started
            threading.Thread(target=ensure_started, daemon=True).start()
            print("[Milvus] autostart thread launched")
    except Exception as e:
        print(f"[Milvus] autostart failed: {e}")
    # 种子化内置风格库/写作指导（失败不阻塞启动）
    try:
        from builtin_library import seed_builtins
        seed_builtins()
        print("[Builtin] seed_builtins() OK")
    except Exception as e:
        print(f"[Builtin] seed failed: {e}")
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
app.include_router(knowledge.router)
app.include_router(settings_router.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=BACKEND_PORT, log_config=None)
