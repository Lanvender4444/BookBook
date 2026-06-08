from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import books, generate, p2p
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
def startup():
    init_db()

@app.get("/api/identity")
def get_identity():
    return {"user_id": generate_user_id()}

app.include_router(books.router)
app.include_router(generate.router)
app.include_router(p2p.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
