import asyncio
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import books, generate, p2p
from routers import providers
from routers.p2p import p2p_service
from services.identity import generate_user_id

# 加载根目录配置
_project_root = Path(__file__).parent.parent
_config_path = _project_root / "config.json"
if _config_path.exists():
    with open(_config_path, "r", encoding="utf-8") as f:
        _config = json.load(f)
else:
    _config = {}

BACKEND_PORT = int(_config.get("backend_port", 8000))
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

    uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT)
