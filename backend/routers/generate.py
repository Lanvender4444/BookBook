import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
from database import get_db
from services.llm_service import generate_outline, generate_chapter
from services.book_builder import save_book
from services.identity import generate_user_id
from models import GenerationHistory

router = APIRouter(prefix="/api/generate", tags=["generate"])

class GenerateRequest(BaseModel):
    prompt: str
    requirements: dict = {}

# 全局存储活跃的生成任务 (用于取消)
active_generations = {}

@router.post("/stream")
async def generate_stream(request: GenerateRequest, db: Session = Depends(get_db)):
    user_id = generate_user_id()
    
    # 创建历史记录
    history = GenerationHistory(
        prompt=request.prompt,
        requirements=request.requirements,
        status="pending",
        author_id=user_id
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    
    history_id = history.id
    
    async def event_generator():
        try:
            # 通知前端历史记录 ID
            yield {"event": "history_id", "data": json.dumps({"history_id": history_id})}
            
            outline = await generate_outline(request.prompt, request.requirements)
            yield {"event": "outline", "data": json.dumps({"type": "outline", "data": outline})}
            
            # 更新大纲到历史记录
            db.query(GenerationHistory).filter(GenerationHistory.id == history_id).update({
                "outline": outline
            })
            db.commit()
            
            chapters = []
            total_chapters = len(outline['chapters'])
            
            for i, chapter in enumerate(outline['chapters']):
                # 检查是否被取消
                if history_id in active_generations and active_generations[history_id] == "cancelled":
                    del active_generations[history_id]
                    yield {"event": "error", "data": json.dumps({"type": "error", "message": "生成已取消"})}
                    db.query(GenerationHistory).filter(GenerationHistory.id == history_id).update({
                        "status": "deleted"
                    })
                    db.commit()
                    return
                
                content = await generate_chapter(outline, chapter, i)
                chapters.append(content)
                
                yield {"event": "chapter", "data": json.dumps({"type": "chapter", "index": i, "data": content})}
            
            book_id = save_book(db, outline, chapters, user_id)
            
            # 更新历史记录状态
            db.query(GenerationHistory).filter(GenerationHistory.id == history_id).update({
                "book_id": book_id,
                "status": "completed",
                "completed_at": datetime.now()
            })
            db.commit()
            
            yield {"event": "done", "data": json.dumps({"type": "done", "book_id": book_id})}
            
        except Exception as e:
            # 更新历史记录为失败
            db.query(GenerationHistory).filter(GenerationHistory.id == history_id).update({
                "status": "failed",
                "error_message": str(e)
            })
            db.commit()
            
            yield {"event": "error", "data": json.dumps({"type": "error", "message": str(e)})}
        finally:
            # 清理活跃任务
            if history_id in active_generations:
                del active_generations[history_id]
    
    return EventSourceResponse(event_generator())

@router.post("/{history_id}/cancel")
async def cancel_generation(history_id: int, db: Session = Depends(get_db)):
    history = db.query(GenerationHistory).filter(GenerationHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    
    if history.status == "pending":
        active_generations[history_id] = "cancelled"
        return {"message": "Cancellation requested"}
    
    return {"message": "Generation not active"}

@router.get("/history")
def get_history(
    status: str = None,
    db: Session = Depends(get_db)
):
    user_id = generate_user_id()
    query = db.query(GenerationHistory).filter(GenerationHistory.author_id == user_id)
    
    if status and status != "all":
        query = query.filter(GenerationHistory.status == status)
    
    return query.order_by(GenerationHistory.created_at.desc()).all()

@router.get("/history/{history_id}")
def get_history_detail(history_id: int, db: Session = Depends(get_db)):
    history = db.query(GenerationHistory).filter(GenerationHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    return history

@router.delete("/history/{history_id}")
def delete_history(history_id: int, db: Session = Depends(get_db)):
    history = db.query(GenerationHistory).filter(GenerationHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    
    if history.status == "pending":
        active_generations[history_id] = "cancelled"
    
    history.status = "deleted"
    db.commit()
    
    return {"message": "History deleted"}
