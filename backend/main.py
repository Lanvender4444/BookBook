import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import books, generate, p2p
from routers.p2p import p2p_service
from services.identity import generate_user_id

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
        print(f"[P2P] TCP server started on port 47833")
    except Exception as e:
        print(f"[P2P] Failed to start TCP server: {e}")

@app.on_event("shutdown")
async def shutdown():
    await p2p_service.stop()

@app.get("/api/identity")
def get_identity():
    return {"user_id": generate_user_id()}

app.include_router(books.router)
app.include_router(generate.router)
app.include_router(p2p.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
