from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.p2p_service import P2PService

router = APIRouter(prefix="/api/peers", tags=["p2p"])

p2p_service = None

def get_p2p_service(db: Session = Depends(get_db)):
    global p2p_service
    if p2p_service is None:
        p2p_service = P2PService(db)
    return p2p_service

@router.get("/")
def list_peers(p2p: P2PService = Depends(get_p2p_service)):
    return p2p.get_peers()

@router.post("/{peer_id}/sync")
async def sync_from_peer(peer_id: str, p2p: P2PService = Depends(get_p2p_service)):
    peers = p2p.get_peers()
    peer = next((p for p in peers if p["id"] == peer_id), None)
    
    if not peer:
        raise HTTPException(status_code=404, detail="Peer not found")
    
    try:
        reader, writer = await __import__('asyncio').open_connection(peer["ip"], 47833)
        writer.write(b'{"action": "get_books"}')
        await writer.drain()
        
        data = await reader.read(65536)
        books = __import__('json').loads(data.decode())
        writer.close()
        
        return {"peer_id": peer_id, "books": books}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.post("/{peer_id}/books/{book_id}")
async def download_book(peer_id: str, book_id: str, p2p: P2PService = Depends(get_p2p_service)):
    peers = p2p.get_peers()
    peer = next((p for p in peers if p["id"] == peer_id), None)
    
    if not peer:
        raise HTTPException(status_code=404, detail="Peer not found")
    
    book_data = await p2p.sync_book(peer["ip"], book_id)
    
    if not book_data:
        raise HTTPException(status_code=500, detail="Failed to download book")
    
    from services.book_builder import save_book as save_p2p_book
    from models import Book, Chapter
    from database import SessionLocal
    
    db = SessionLocal()
    try:
        existing = db.query(Book).filter(Book.id == book_data["id"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Book already exists")
        
        new_book = Book(
            id=book_data["id"],
            title=book_data["title"],
            description=book_data["description"],
            outline=book_data["outline"],
            source="p2p",
            peer_origin=peer_id
        )
        db.add(new_book)
        db.flush()
        
        for ch in book_data["chapters"]:
            chapter = Chapter(
                book_id=book_data["id"],
                index=ch["index"],
                title=ch["title"],
                content=ch["content"]
            )
            db.add(chapter)
        
        db.commit()
        return {"message": "Book downloaded successfully", "book_id": book_data["id"]}
        
    finally:
        db.close()
