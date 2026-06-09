from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from services.book_builder import (
    get_book, get_all_books, delete_book, 
    export_to_markdown, get_book_chapters, update_books_dir
)
from config import BOOKS_DIR

router = APIRouter(prefix="/api/books", tags=["books"])

class UpdateDirRequest(BaseModel):
    path: str

@router.get("/")
def list_books(db: Session = Depends(get_db)):
    return get_all_books(db)

@router.get("/{book_id}")
def get_book_detail(book_id: str, db: Session = Depends(get_db)):
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {
        "id": book.id,
        "title": book.title,
        "description": book.description,
        "outline": book.outline,
        "file_path": book.file_path,
        "created_at": book.created_at.isoformat() if book.created_at else None,
        "author_id": book.author_id,
        "source": book.source,
        "peer_origin": book.peer_origin,
        "language": book.language
    }

@router.get("/{book_id}/chapters")
def get_book_chapters_api(book_id: str, db: Session = Depends(get_db)):
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return get_book_chapters(db, book_id)

@router.delete("/{book_id}")
def remove_book(book_id: str, db: Session = Depends(get_db)):
    if not delete_book(db, book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}

@router.get("/{book_id}/export")
def export_book(book_id: str, format: str = "markdown", db: Session = Depends(get_db)):
    if format == "markdown":
        content = export_to_markdown(db, book_id)
        if not content:
            raise HTTPException(status_code=404, detail="Book not found")
        return {"content": content}
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

@router.get("/config/dir")
def get_books_dir():
    return {"dir": BOOKS_DIR}

@router.post("/config/dir")
def set_books_dir(request: UpdateDirRequest):
    try:
        update_books_dir(request.path)
        return {"message": "Directory updated", "dir": request.path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
