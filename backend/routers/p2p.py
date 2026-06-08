from fastapi import APIRouter, HTTPException
from database import SessionLocal
from services.p2p_service import P2PService
from services.book_builder import save_book as save_p2p_book, get_book
from models import Book
from pydantic import BaseModel

router = APIRouter(prefix="/api/peers", tags=["p2p"])

p2p_service = P2PService()


class ConnectRequest(BaseModel):
    host: str
    port: int = 47833

class ShareRequest(BaseModel):
    book_id: str = None
    expires_hours: int = 24

class RedeemRequest(BaseModel):
    token: str
    host: str
    port: int = 47833


@router.get("/")
def list_peers():
    return []

@router.post("/connect")
async def connect_to_peer(req: ConnectRequest):
    result = await p2p_service.connect_to_peer(req.host, req.port)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Connection failed"))
    return result

@router.post("/{peer_host}/books")
async def fetch_peer_books(peer_host: str, port: int = 47833):
    books = await p2p_service.fetch_book_list(peer_host, port)
    return {"books": books}

@router.post("/{peer_host}/books/{book_id}/download")
async def download_book_from_peer(peer_host: str, book_id: str, port: int = 47833):
    book_data = await p2p_service.fetch_book(peer_host, book_id, port)
    if not book_data:
        raise HTTPException(status_code=404, detail="Book not found on peer")
    
    db = SessionLocal()
    try:
        existing = db.query(Book).filter(Book.id == book_data["id"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Book already exists")
        
        saved_id = save_p2p_book(db, book_data, book_data.get("author_id", "p2p"))
        return {"message": "Book downloaded successfully", "book_id": saved_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/share")
def create_share_token(req: ShareRequest):
    result = p2p_service.create_share_token(book_id=req.book_id, expires_hours=req.expires_hours)
    return result

@router.get("/share/{token}")
def get_share_info(token: str):
    info = p2p_service.get_share_info(token)
    if not info:
        raise HTTPException(status_code=404, detail="Share token not found or expired")
    
    book_info = None
    if info["book_id"]:
        db = SessionLocal()
        try:
            book = get_book(db, info["book_id"])
            if book:
                book_info = {
                    "id": book.id,
                    "title": book.title,
                    "description": book.description
                }
        finally:
            db.close()
    
    return {
        "token": info["token"],
        "book_id": info["book_id"],
        "book": book_info,
        "peer_id": info["peer_id"],
        "created_at": info["created_at"],
        "expires_at": info["expires_at"]
    }

@router.post("/redeem")
async def redeem_share_token(req: RedeemRequest):
    share_info = p2p_service.get_share_info(req.token)
    if not share_info:
        raise HTTPException(status_code=404, detail="Share token not found or expired")
    
    book_data = await p2p_service.fetch_by_share_token(req.host, req.token, req.port)
    if not book_data:
        raise HTTPException(status_code=404, detail="Failed to fetch book from peer")
    
    db = SessionLocal()
    try:
        existing = db.query(Book).filter(Book.id == book_data["id"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Book already exists")
        
        saved_id = save_p2p_book(db, book_data, book_data.get("author_id", "p2p"))
        return {"message": "Book downloaded successfully", "book_id": saved_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/sync")
async def sync_from_peer(peer_host: str = None, port: int = 47833):
    if not peer_host:
        raise HTTPException(status_code=400, detail="peer_host is required")
    
    books = await p2p_service.fetch_book_list(peer_host, port)
    return {"books": books}