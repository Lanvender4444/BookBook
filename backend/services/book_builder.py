import uuid
import json
import re
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from models import Book
from config import BOOKS_DIR, ensure_books_dir

def sanitize_filename(name: str) -> str:
    """清理文件名，移除非法字符"""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.strip()[:100]  # 限制长度
    return name if name else "untitled"

def get_book_filepath(book_id: str, title: str) -> Path:
    """获取书籍文件保存路径"""
    ensure_books_dir()
    safe_title = sanitize_filename(title)
    filename = f"{book_id}_{safe_title}.md"
    return Path(BOOKS_DIR) / filename

def save_book(db: Session, outline: dict, chapters: list, user_id: str) -> str:
    """保存书籍到本地文件和数据库"""
    book_id = str(uuid.uuid4())[:8]  # 短 ID
    
    # 生成 Markdown 内容
    md_content = f"# {outline['title']}\n\n"
    md_content += f"{outline['description']}\n\n---\n\n"
    
    for i, (chapter_data, content) in enumerate(zip(outline['chapters'], chapters)):
        md_content += f"## 第{i+1}章：{chapter_data['title']}\n\n{content}\n\n"
    
    # 保存到本地文件
    filepath = get_book_filepath(book_id, outline['title'])
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # 保存到数据库
    book = Book(
        id=book_id,
        title=outline['title'],
        description=outline['description'],
        outline=outline,
        file_path=str(filepath),
        author_id=user_id,
        source="local"
    )
    db.add(book)
    db.commit()
    
    return book_id

def save_p2p_book(db: Session, book_data: dict, peer_id: str) -> str:
    """保存 P2P 接收的书籍"""
    book_id = book_data['id']
    
    # 生成 Markdown 内容
    md_content = f"# {book_data['title']}\n\n"
    md_content += f"{book_data['description']}\n\n---\n\n"
    
    for ch in book_data.get('chapters', []):
        md_content += f"## {ch['title']}\n\n{ch['content']}\n\n"
    
    # 保存到本地文件
    filepath = get_book_filepath(book_id, book_data['title'])
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # 保存到数据库
    book = Book(
        id=book_id,
        title=book_data['title'],
        description=book_data['description'],
        outline=book_data.get('outline', {}),
        file_path=str(filepath),
        source="p2p",
        peer_origin=peer_id
    )
    db.add(book)
    db.commit()
    
    return book_id

def get_book(db: Session, book_id: str):
    return db.query(Book).filter(Book.id == book_id).first()

def get_all_books(db: Session):
    return db.query(Book).order_by(Book.created_at.desc()).all()

def delete_book(db: Session, book_id: str) -> bool:
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        # 删除本地文件
        filepath = Path(book.file_path)
        if filepath.exists():
            filepath.unlink()
        
        db.delete(book)
        db.commit()
        return True
    return False

def get_book_content(db: Session, book_id: str) -> str:
    """读取书籍文件内容"""
    book = get_book(db, book_id)
    if not book:
        return None
    
    filepath = Path(book.file_path)
    if not filepath.exists():
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def get_book_chapters(db: Session, book_id: str) -> list:
    """从 Markdown 内容解析章节"""
    content = get_book_content(db, book_id)
    if not content:
        return []
    
    chapters = []
    # 按 ## 分割章节
    parts = re.split(r'\n## ', content)
    
    for i, part in enumerate(parts):
        if i == 0:
            continue  # 跳过标题部分
        
        lines = part.strip().split('\n', 1)
        title = lines[0].strip()
        chapter_content = lines[1].strip() if len(lines) > 1 else ""
        
        # 移除章节标题中的"第X章："前缀
        title = re.sub(r'^第\d+章：?', '', title).strip()
        
        chapters.append({
            'index': i - 1,
            'title': title,
            'content': chapter_content
        })
    
    return chapters

def export_to_markdown(db: Session, book_id: str) -> str:
    """导出为 Markdown"""
    return get_book_content(db, book_id)

def update_books_dir(new_dir: str):
    """更新书籍保存目录"""
    import os
    os.environ['BOOKS_DIR'] = new_dir
    ensure_books_dir()
