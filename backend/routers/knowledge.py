"""知识源（RAG）与写作卡 API。"""

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import KnowledgeSource, KnowledgeChunk, WritingCard
from services.rag_service import CATEGORIES, index_source, retrieve, new_id
from utils import get_app_data_dir

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

KNOWLEDGE_DIR = get_app_data_dir() / "knowledge"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_SUFFIXES = {".txt", ".md", ".markdown", ".text", ".pdf", ".docx", ".epub"}


def _source_to_dict(s: KnowledgeSource) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "category": s.category,
        "link_mode": s.link_mode,
        "file_path": s.file_path,
        "has_text": bool(s.text_content),
        "prompt": s.prompt,
        "language": s.language,
        "builtin": s.builtin,
        "index_status": s.index_status,
        "index_error": s.index_error,
        "chunk_count": s.chunk_count,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


# ---------------------------------------------------------------- 知识源

@router.get("/sources")
def list_sources(category: str | None = None, db: Session = Depends(get_db)):
    q = db.query(KnowledgeSource)
    if category:
        q = q.filter(KnowledgeSource.category == category)
    return [_source_to_dict(s) for s in q.order_by(KnowledgeSource.created_at.desc()).all()]


@router.post("/sources/upload")
async def upload_source(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(None),
    category: str = Form(...),
    prompt: str = Form(""),
    language: str = Form(""),
    db: Session = Depends(get_db),
):
    """上传文件投递（copy 模式：复制到应用数据目录）。"""
    if category not in CATEGORIES:
        raise HTTPException(400, f"category 必须是 {CATEGORIES}")
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(400, f"不支持的格式 {suffix}，支持: txt/md/pdf/docx/epub")

    sid = new_id()
    dest = KNOWLEDGE_DIR / f"{sid}{suffix}"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    source = KnowledgeSource(
        id=sid,
        name=name or Path(file.filename).stem,
        category=category,
        link_mode="copy",
        file_path=str(dest),
        prompt=prompt or None,
        language=language or None,
    )
    db.add(source)
    db.commit()
    background.add_task(index_source, sid)
    return _source_to_dict(source)


class LinkSourceRequest(BaseModel):
    path: str
    category: str
    name: str | None = None
    prompt: str = ""
    language: str = ""


@router.post("/sources/link")
def link_source(req: LinkSourceRequest, background: BackgroundTasks, db: Session = Depends(get_db)):
    """链接投递（link 模式：引用原路径，不复制，类似软链接）。"""
    if req.category not in CATEGORIES:
        raise HTTPException(400, f"category 必须是 {CATEGORIES}")
    path = Path(req.path)
    if not path.exists() or not path.is_file():
        raise HTTPException(400, f"文件不存在: {req.path}")
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise HTTPException(400, f"不支持的格式 {path.suffix}")

    sid = new_id()
    source = KnowledgeSource(
        id=sid,
        name=req.name or path.stem,
        category=req.category,
        link_mode="link",
        file_path=str(path),
        prompt=req.prompt or None,
        language=req.language or None,
    )
    db.add(source)
    db.commit()
    background.add_task(index_source, sid)
    return _source_to_dict(source)


class TextSourceRequest(BaseModel):
    name: str
    category: str
    content: str
    prompt: str = ""
    language: str = ""


@router.post("/sources/text")
def create_text_source(req: TextSourceRequest, background: BackgroundTasks, db: Session = Depends(get_db)):
    """纯文本投递（直接粘贴内容）。"""
    if req.category not in CATEGORIES:
        raise HTTPException(400, f"category 必须是 {CATEGORIES}")
    if not req.content.strip():
        raise HTTPException(400, "内容为空")
    sid = new_id()
    source = KnowledgeSource(
        id=sid,
        name=req.name,
        category=req.category,
        link_mode="copy",
        text_content=req.content,
        prompt=req.prompt or None,
        language=req.language or None,
    )
    db.add(source)
    db.commit()
    background.add_task(index_source, sid)
    return _source_to_dict(source)


class UpdateSourceRequest(BaseModel):
    name: str | None = None
    prompt: str | None = None
    language: str | None = None


@router.patch("/sources/{source_id}")
def update_source(source_id: str, req: UpdateSourceRequest, db: Session = Depends(get_db)):
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    if not source:
        raise HTTPException(404, "知识源不存在")
    if source.builtin:
        raise HTTPException(400, "内置知识源不可修改，可复制后编辑")
    if req.name is not None:
        source.name = req.name
    if req.prompt is not None:
        source.prompt = req.prompt or None
    if req.language is not None:
        source.language = req.language or None
    db.commit()
    return _source_to_dict(source)


@router.delete("/sources/{source_id}")
def delete_source(source_id: str, db: Session = Depends(get_db)):
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    if not source:
        raise HTTPException(404, "知识源不存在")
    if source.builtin:
        raise HTTPException(400, "内置知识源不可删除")
    db.query(KnowledgeChunk).filter(KnowledgeChunk.source_id == source_id).delete()
    # copy 模式删除托管副本；link 模式不动原文件
    if source.link_mode == "copy" and source.file_path:
        try:
            Path(source.file_path).unlink(missing_ok=True)
        except OSError:
            pass
    db.delete(source)
    db.commit()
    return {"ok": True}


@router.post("/sources/{source_id}/reindex")
def reindex_source(source_id: str, background: BackgroundTasks, db: Session = Depends(get_db)):
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    if not source:
        raise HTTPException(404, "知识源不存在")
    background.add_task(index_source, source_id)
    return {"ok": True, "status": "indexing"}


class SearchRequest(BaseModel):
    query: str
    source_ids: list[str]
    top_k: int = 5


@router.post("/search")
def search(req: SearchRequest):
    """调试/预览检索结果。"""
    return retrieve(req.query, req.source_ids, req.top_k)


# ---------------------------------------------------------------- 写作卡

def _card_to_dict(c: WritingCard) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "writing_guide_ids": c.writing_guide_ids or [],
        "style_ids": c.style_ids or [],
        "reference_ids": c.reference_ids or [],
        "continuation_ids": c.continuation_ids or [],
        "extra_requirements": c.extra_requirements or "",
        "tags": c.tags or [],
        "builtin": c.builtin,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


class CardRequest(BaseModel):
    name: str
    writing_guide_ids: list[str] = []
    style_ids: list[str] = []
    reference_ids: list[str] = []
    continuation_ids: list[str] = []
    extra_requirements: str = ""
    tags: list[str] = []


def _validate_card_sources(req: CardRequest, db: Session):
    all_ids = (
        req.writing_guide_ids + req.style_ids + req.reference_ids + req.continuation_ids
    )
    if not all_ids:
        return
    found = {
        s.id
        for s in db.query(KnowledgeSource).filter(KnowledgeSource.id.in_(all_ids)).all()
    }
    missing = set(all_ids) - found
    if missing:
        raise HTTPException(400, f"知识源不存在: {sorted(missing)}")


@router.get("/cards")
def list_cards(db: Session = Depends(get_db)):
    return [
        _card_to_dict(c)
        for c in db.query(WritingCard).order_by(WritingCard.created_at.desc()).all()
    ]


@router.post("/cards")
def create_card(req: CardRequest, db: Session = Depends(get_db)):
    if not req.name.strip():
        raise HTTPException(400, "名称不能为空")
    _validate_card_sources(req, db)
    card = WritingCard(
        id=new_id(),
        name=req.name.strip(),
        writing_guide_ids=req.writing_guide_ids,
        style_ids=req.style_ids,
        reference_ids=req.reference_ids,
        continuation_ids=req.continuation_ids,
        extra_requirements=req.extra_requirements or None,
        tags=[t.strip().lstrip("#").strip() for t in req.tags if t.strip().lstrip("#").strip()],
    )
    db.add(card)
    db.commit()
    return _card_to_dict(card)


@router.put("/cards/{card_id}")
def update_card(card_id: str, req: CardRequest, db: Session = Depends(get_db)):
    card = db.query(WritingCard).filter(WritingCard.id == card_id).first()
    if not card:
        raise HTTPException(404, "写作卡不存在")
    if card.builtin:
        raise HTTPException(400, "内置写作卡不可修改，可复制后编辑")
    _validate_card_sources(req, db)
    card.name = req.name.strip() or card.name
    card.writing_guide_ids = req.writing_guide_ids
    card.style_ids = req.style_ids
    card.reference_ids = req.reference_ids
    card.continuation_ids = req.continuation_ids
    card.extra_requirements = req.extra_requirements or None
    card.tags = [t.strip().lstrip("#").strip() for t in req.tags if t.strip().lstrip("#").strip()]
    db.commit()
    return _card_to_dict(card)


@router.delete("/cards/{card_id}")
def delete_card(card_id: str, db: Session = Depends(get_db)):
    card = db.query(WritingCard).filter(WritingCard.id == card_id).first()
    if not card:
        raise HTTPException(404, "写作卡不存在")
    if card.builtin:
        raise HTTPException(400, "内置写作卡不可删除")
    db.delete(card)
    db.commit()
    return {"ok": True}


@router.post("/cards/{card_id}/duplicate")
def duplicate_card(card_id: str, db: Session = Depends(get_db)):
    card = db.query(WritingCard).filter(WritingCard.id == card_id).first()
    if not card:
        raise HTTPException(404, "写作卡不存在")
    copy = WritingCard(
        id=new_id(),
        name=f"{card.name} (副本)",
        writing_guide_ids=list(card.writing_guide_ids or []),
        style_ids=list(card.style_ids or []),
        reference_ids=list(card.reference_ids or []),
        continuation_ids=list(card.continuation_ids or []),
        extra_requirements=card.extra_requirements,
        tags=list(card.tags or []),
        builtin=False,
    )
    db.add(copy)
    db.commit()
    return _card_to_dict(copy)
