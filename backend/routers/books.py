import os
import shutil
import subprocess
from pathlib import Path
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

def _find_app_executable(app_name: str) -> str:
    """查找应用可执行文件路径，支持常见安装位置、PATH 和注册表"""
    app_lower = app_name.lower().strip()

    # 1. 尝试在 PATH 中查找
    path_found = shutil.which(app_name)
    if path_found:
        return path_found

    # 2. 常见安装路径
    common_paths = {
        'typora': [
            r'C:\Program Files\Typora\Typora.exe',
            r'C:\Program Files (x86)\Typora\Typora.exe',
            os.path.expandvars(r'%LOCALAPPDATA%\Programs\Typora\Typora.exe'),
            os.path.expandvars(r'%USERPROFILE%\AppData\Local\Programs\Typora\Typora.exe'),
            os.path.expandvars(r'%USERPROFILE%\scoop\apps\typora\current\Typora.exe'),
        ]
    }

    if app_lower in common_paths:
        for p in common_paths[app_lower]:
            if Path(p).exists():
                return p

    # 3. Windows 注册表查找
    if os.name == 'nt' and app_lower == 'typora':
        try:
            import winreg
            for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                for key_path in [
                    r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Typora.exe',
                    r'SOFTWARE\Typora',
                ]:
                    try:
                        with winreg.OpenKey(hive, key_path) as key:
                            val, _ = winreg.QueryValueEx(key, None)
                            if val and Path(val).exists():
                                return val
                    except FileNotFoundError:
                        continue
        except Exception:
            pass

    return None

@router.post("/{book_id}/open")
def open_book_local(book_id: str, app: str = None, db: Session = Depends(get_db)):
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    filepath = Path(book.file_path)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Book file not found")

    try:
        if app:
            app_lower = app.lower().strip()
            found = _find_app_executable(app)
            if found:
                subprocess.Popen([found, str(filepath)], shell=False)
            else:
                # 作为命令直接尝试
                subprocess.Popen(f'{app} "{str(filepath)}"', shell=True)
        else:
            if os.name == 'nt':
                os.startfile(str(filepath))
            else:
                subprocess.Popen(['open', str(filepath)])
        return {"message": "Book opened successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
