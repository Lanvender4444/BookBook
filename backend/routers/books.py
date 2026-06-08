from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.book_builder import get_book, get_all_books, delete_book, export_to_markdown

router = APIRouter(prefix="/api/books", tags=["books"])

@router.get("/")
def list_books(db: Session = Depends(get_db)):
    return get_all_books(db)

@router.get("/{book_id}")
def get_book_detail(book_id: str, db: Session = Depends(get_db)):
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

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
