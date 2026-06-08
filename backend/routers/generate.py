import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
from database import get_db
from services.llm_service import generate_outline, generate_chapter
from services.book_builder import save_book
from services.identity import generate_user_id

router = APIRouter(prefix="/api/generate", tags=["generate"])

class GenerateRequest(BaseModel):
    prompt: str
    requirements: dict = {}

class GenerationStatus:
    def __init__(self):
        self.statuses = {}
        
    def set_status(self, gen_id: str, status: dict):
        self.statuses[gen_id] = status
        
    def get_status(self, gen_id: str):
        return self.statuses.get(gen_id)

generation_status = GenerationStatus()

@router.post("/stream")
async def generate_stream(request: GenerateRequest, db: Session = Depends(get_db)):
    async def event_generator():
        try:
            generation_status.set_status("current", {"step": "outline", "progress": 0})
            
            outline = await generate_outline(request.prompt, request.requirements)
            yield f"data: {json.dumps({'type': 'outline', 'data': outline})}\n\n"
            
            chapters = []
            total_chapters = len(outline['chapters'])
            
            for i, chapter in enumerate(outline['chapters']):
                generation_status.set_status("current", {
                    "step": "chapter",
                    "progress": (i + 1) / total_chapters * 100,
                    "current_chapter": i + 1,
                    "total_chapters": total_chapters
                })
                
                content = await generate_chapter(outline, chapter, i)
                chapters.append(content)
                
                yield f"data: {json.dumps({'type': 'chapter', 'index': i, 'data': content})}\n\n"
            
            user_id = generate_user_id()
            book_id = save_book(db, outline, chapters, user_id)
            
            generation_status.set_status("current", {
                "step": "done",
                "book_id": book_id,
                "progress": 100
            })
            
            yield f"data: {json.dumps({'type': 'done', 'book_id': book_id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return EventSourceResponse(event_generator())

@router.get("/status/{gen_id}")
def get_generation_status(gen_id: str):
    status = generation_status.get_status(gen_id)
    if not status:
        raise HTTPException(status_code=404, detail="Generation not found")
    return status
