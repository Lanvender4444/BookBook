import uuid
import json
from datetime import datetime
from sqlalchemy.orm import Session
from models import Book, Chapter

def save_book(db: Session, outline: dict, chapters: list, user_id: str) -> str:
    book_id = str(uuid.uuid4())
    
    book = Book(
        id=book_id,
        title=outline["title"],
        description=outline["description"],
        outline=outline,
        author_id=user_id,
        source="local"
    )
    db.add(book)
    db.flush()
    
    for i, (chapter_data, content) in enumerate(zip(outline["chapters"], chapters)):
        chapter = Chapter(
            book_id=book_id,
            index=i,
            title=chapter_data["title"],
            content=content
        )
        db.add(chapter)
    
    db.commit()
    return book_id

def get_book(db: Session, book_id: str):
    return db.query(Book).filter(Book.id == book_id).first()

def get_all_books(db: Session):
    return db.query(Book).order_by(Book.created_at.desc()).all()

def delete_book(db: Session, book_id: str) -> bool:
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        db.delete(book)
        db.commit()
        return True
    return False

def get_book_chapters(db: Session, book_id: str):
    return db.query(Chapter).filter(Chapter.book_id == book_id).order_by(Chapter.index).all()

def export_to_markdown(db: Session, book_id: str) -> str:
    book = get_book(db, book_id)
    if not book:
        return None
    
    chapters = get_book_chapters(db, book_id)
    md_content = f"# {book.title}\n\n"
    md_content += f"{book.description}\n\n---\n\n"
    
    for chapter in chapters:
        md_content += f"## {chapter.title}\n\n{chapter.content}\n\n"
    
    return md_content
