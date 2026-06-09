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
    local_host: str = None


@router.get("/")
def list_peers():
    return []

@router.get("/info")
def get_node_info():
    """获取当前 P2P 节点信息（IP、User ID 等）"""
    return {
        "user_id": p2p_service.user_id,
        "host": p2p_service.get_local_ip(),
        "port": p2p_service.__class__.__name__  # fallback, actual port from config
    }

# 更准确的 info endpoint
@router.get("/me")
def get_my_info():
    from config import P2P_PORT
    local_ip = p2p_service.get_local_ip()
    public_ip = p2p_service.get_public_ip()
    return {
        "user_id": p2p_service.user_id,
        "host": local_ip,
        "port": P2P_PORT,
        "public_ip": public_ip,
        "nat_type": "public" if public_ip else "local"
    }

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

@router.get("/shares")
def list_share_tokens():
    """列出所有有效的分享链接"""
    shares = p2p_service.get_all_shares(include_expired=False)
    return {"shares": shares}

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
        "expires_at": info["expires_at"],
        "host": info["host"],
        "public_host": info.get("public_host", ""),
        "port": info["port"]
    }

@router.post("/redeem")
async def redeem_share_token(req: RedeemRequest):
    share_info = p2p_service.get_share_info(req.token)
    if not share_info:
        raise HTTPException(status_code=404, detail="Share token not found or expired")

    # 优先尝试局域网地址，失败再尝试公网地址
    hosts_to_try = []
    if req.local_host:
        hosts_to_try.append(req.local_host)
    if req.host:
        hosts_to_try.append(req.host)

    result = None
    last_error = None
    for host in hosts_to_try:
        try:
            result = await p2p_service.fetch_by_share_token(host, req.token, req.port)
            if result:
                break
        except Exception as e:
            last_error = str(e)

    if not result:
        detail = "Failed to fetch book from peer"
        if last_error:
            detail += f": {last_error}"
        raise HTTPException(status_code=404, detail=detail)

    db = SessionLocal()
    try:
        saved_ids = []

        # 处理单本书
        if "book" in result:
            book_data = result["book"]
            existing = db.query(Book).filter(Book.id == book_data["id"]).first()
            if existing:
                raise HTTPException(status_code=400, detail="Book already exists")
            saved_id = save_p2p_book(db, book_data, book_data.get("author_id", "p2p"))
            saved_ids.append(saved_id)
            return {"message": "Book downloaded successfully", "book_id": saved_id, "saved_ids": saved_ids}

        # 处理多本书（all_books 模式）
        if result.get("all_books") and "books" in result:
            books_meta = result["books"]
            failed = []
            for meta in books_meta:
                try:
                    existing = db.query(Book).filter(Book.id == meta["id"]).first()
                    if existing:
                        continue
                    # 获取每本书的完整内容（优先局域网地址）
                    book_data = None
                    for host in hosts_to_try:
                        book_data = await p2p_service.fetch_book(host, meta["id"], req.port)
                        if book_data:
                            break
                    if book_data:
                        saved_id = save_p2p_book(db, book_data, book_data.get("author_id", "p2p"))
                        saved_ids.append(saved_id)
                except Exception as e:
                    failed.append({"id": meta.get("id"), "error": str(e)})

            if not saved_ids:
                raise HTTPException(status_code=404, detail="No books could be downloaded")

            return {
                "message": f"Downloaded {len(saved_ids)} books successfully",
                "saved_ids": saved_ids,
                "failed": failed
            }

        raise HTTPException(status_code=404, detail="Invalid response from peer")
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