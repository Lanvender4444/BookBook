import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from services.llm_service import generate_outline, generate_chapter
from services.book_builder import save_book
from services.identity import generate_user_id
from models import GenerationHistory

router = APIRouter(prefix="/api/generate", tags=["generate"])


class GenerateRequest(BaseModel):
    prompt: str
    requirements: dict = {}
    provider_id: str | None = None
    model_name: str | None = None
    card_id: str | None = None  # 写作卡
    extra_requirements: str = ""  # 临时额外需求（与写作卡的额外需求合并）
    tags: list[str] = []  # 用户自填标签；留空则用 AI 生成的标签


def _load_card(card_id: str | None):
    if not card_id:
        return None
    from models import WritingCard

    db = SessionLocal()
    try:
        return db.query(WritingCard).filter(WritingCard.id == card_id).first()
    finally:
        db.close()


def _card_context_for(card, query: str, request_extra: str = "") -> dict:
    """组装写作卡上下文；无卡时返回空上下文。"""
    if card is None:
        return {
            "card_context": "",
            "extra_requirements": request_extra.strip(),
            "has_continuation": False,
        }
    from services.rag_service import build_card_context

    try:
        ctx = build_card_context(card, query)
    except Exception as e:
        print(f"[RAG] build_card_context failed: {e}")
        ctx = {"context_block": "", "extra_requirements": card.extra_requirements or "", "has_continuation": False}
    extras = [x for x in (ctx.get("extra_requirements", ""), request_extra.strip()) if x]
    return {
        "card_context": ctx.get("context_block", ""),
        "extra_requirements": "\n".join(extras),
        "has_continuation": ctx.get("has_continuation", False),
    }


# 后台任务状态存储
# 结构: {history_id: {"status": "running"|"completed"|"failed", "progress": {...}, "event": asyncio.Event}}
task_status = {}

import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)


def run_generation_task(
    history_id: int,
    prompt: str,
    requirements: dict,
    user_id: str,
    language: str = "zh-CN",
    provider_id: str = None,
    model_name: str = None,
    card_id: str = None,
    extra_requirements: str = "",
    user_tags: list = None,
):
    """在后台线程中运行生成任务"""
    from services.llm_service import generate_outline_sync, generate_chapter_sync
    from services.book_builder import save_book_sync

    db = SessionLocal()
    try:
        # 更新状态为运行中
        task_status[history_id] = {
            "status": "running",
            "progress": {"stage": "outline", "message": "正在生成大纲..."},
            "cancelled": False,
        }

        # 生成大纲前检查取消
        if task_status.get(history_id, {}).get("cancelled"):
            db.query(GenerationHistory).filter(
                GenerationHistory.id == history_id
            ).update({"status": "deleted"})
            db.commit()
            task_status[history_id]["status"] = "cancelled"
            return

        # 写作卡：检索 RAG 上下文（大纲阶段以用户需求为检索词）
        card = _load_card(card_id)
        outline_ctx = _card_context_for(card, prompt, extra_requirements)

        # 生成大纲（耗时操作，无法中断）
        outline = generate_outline_sync(
            prompt,
            requirements,
            provider_id=provider_id,
            model_name=model_name,
            card_context=outline_ctx["card_context"],
            extra_requirements=outline_ctx["extra_requirements"],
            has_continuation=outline_ctx["has_continuation"],
        )

        # 大纲生成后再次检查取消
        if task_status.get(history_id, {}).get("cancelled"):
            db.query(GenerationHistory).filter(
                GenerationHistory.id == history_id
            ).update({"status": "deleted"})
            db.commit()
            task_status[history_id]["status"] = "cancelled"
            return

        # 更新大纲到历史记录
        db.query(GenerationHistory).filter(GenerationHistory.id == history_id).update(
            {"outline": outline, "status": "pending"}
        )
        db.commit()

        task_status[history_id]["progress"] = {
            "stage": "outline_done",
            "message": f"大纲生成完成: {outline.get('title', '')}",
            "outline": outline,
        }

        chapters = []
        total_chapters = len(outline["chapters"])

        for i, chapter in enumerate(outline["chapters"]):
            # 每个章节开始前检查取消
            if task_status.get(history_id, {}).get("cancelled"):
                db.query(GenerationHistory).filter(
                    GenerationHistory.id == history_id
                ).update({"status": "deleted"})
                db.commit()
                task_status[history_id]["status"] = "cancelled"
                return

            # 更新进度
            task_status[history_id]["progress"] = {
                "stage": "chapter",
                "message": f"正在生成第 {i + 1}/{total_chapters} 章: {chapter.get('title', '')}",
                "current_chapter": i,
                "total_chapters": total_chapters,
                "chapter_title": chapter.get("title", ""),
            }

            # 写作卡：每章按「章节标题+概要」重新检索，上下文更精准
            chapter_query = f"{chapter.get('title', '')} {chapter.get('summary', '')}".strip() or prompt
            chapter_ctx = _card_context_for(card, chapter_query, extra_requirements)

            # 生成章节（耗时操作，无法中断）
            content = generate_chapter_sync(
                outline,
                chapter,
                i,
                provider_id=provider_id,
                model_name=model_name,
                language=language,
                card_context=chapter_ctx["card_context"],
                extra_requirements=chapter_ctx["extra_requirements"],
                has_continuation=chapter_ctx["has_continuation"],
            )
            chapters.append(content)

            # 章节完成后检查取消
            if task_status.get(history_id, {}).get("cancelled"):
                db.query(GenerationHistory).filter(
                    GenerationHistory.id == history_id
                ).update({"status": "deleted"})
                db.commit()
                task_status[history_id]["status"] = "cancelled"
                return

            # 章节完成，更新进度
            task_status[history_id]["progress"] = {
                "stage": "chapter_done",
                "message": f"第 {i + 1} 章完成",
                "current_chapter": i + 1,
                "total_chapters": total_chapters,
                "chapter_title": chapter.get("title", ""),
                "chapter_content": content,
            }

        # 保存书籍（标签 = 用户标签 + AI 标签，去重）
        ai_tags = outline.get("tags") or []
        merged_tags = list(dict.fromkeys([*(user_tags or []), *ai_tags]))
        book_id = save_book_sync(db, outline, chapters, user_id, language, tags=merged_tags)

        # 更新历史记录状态
        db.query(GenerationHistory).filter(GenerationHistory.id == history_id).update(
            {"book_id": book_id, "status": "completed", "completed_at": datetime.now()}
        )
        db.commit()

        task_status[history_id] = {
            "status": "completed",
            "progress": {
                "stage": "done",
                "message": "生成完成",
                "book_id": book_id,
                "book_title": outline.get("title", "未命名电子书"),
            },
        }

    except Exception as e:
        # 更新历史记录为失败
        db.query(GenerationHistory).filter(GenerationHistory.id == history_id).update(
            {"status": "failed", "error_message": str(e)}
        )
        db.commit()

        task_status[history_id] = {
            "status": "failed",
            "progress": {"stage": "error", "message": str(e)},
        }
    finally:
        db.close()


@router.post("/stream")
async def generate_stream(request: GenerateRequest, db: Session = Depends(get_db)):
    user_id = generate_user_id()

    # 从 requirements 中提取语言信息
    language = request.requirements.get("language", "zh-CN")

    # 创建历史记录
    history = GenerationHistory(
        prompt=request.prompt,
        requirements=request.requirements,
        status="pending",
        author_id=user_id,
        language=language,
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    history_id = history.id

    # 启动后台任务（不依赖SSE连接）
    task_status[history_id] = {
        "status": "starting",
        "progress": {"stage": "starting", "message": "准备开始..."},
        "cancelled": False,
    }

    # 在后台线程中运行任务
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        executor,
        run_generation_task,
        history_id,
        request.prompt,
        request.requirements,
        user_id,
        language,
        request.provider_id,
        request.model_name,
        request.card_id,
        request.extra_requirements,
        request.tags,
    )

    async def event_generator():
        last_update_hash = None

        try:
            # 通知前端历史记录 ID
            yield {
                "event": "history_id",
                "data": json.dumps({"history_id": history_id}),
            }

            while True:
                status_info = task_status.get(history_id)

                if not status_info:
                    await asyncio.sleep(0.5)
                    continue

                current_status = status_info["status"]
                progress = status_info["progress"]

                # 创建进度的hash用于检测变化
                update_hash = f"{current_status}:{progress.get('stage')}:{progress.get('current_chapter', 0)}"

                # 只在状态变化时发送更新
                if update_hash != last_update_hash:
                    yield {
                        "event": "progress",
                        "data": json.dumps(
                            {
                                "type": "progress",
                                "status": current_status,
                                "data": progress,
                            }
                        ),
                    }
                    last_update_hash = update_hash

                # 如果任务完成或失败，退出循环
                if current_status in ("completed", "failed", "cancelled"):
                    final_event = "done" if current_status == "completed" else "error"
                    yield {
                        "event": final_event,
                        "data": json.dumps({"type": final_event, "data": progress}),
                    }
                    break

                await asyncio.sleep(0.3)  # 轮询间隔

        except asyncio.CancelledError:
            # SSE连接断开，但任务继续运行
            pass
        finally:
            # 不删除task_status，让任务继续运行
            pass

    return EventSourceResponse(event_generator())


@router.get("/stream/{history_id}")
async def reconnect_stream(history_id: int, db: Session = Depends(get_db)):
    """重新连接到正在进行的任务"""
    history = (
        db.query(GenerationHistory).filter(GenerationHistory.id == history_id).first()
    )
    if not history:
        raise HTTPException(status_code=404, detail="History not found")

    async def event_generator():
        last_update_hash = None
        no_task_count = 0
        max_no_task_wait = 60

        try:
            yield {
                "event": "history_id",
                "data": json.dumps({"history_id": history_id}),
            }

            if history.outline:
                outline = history.outline
                yield {
                    "event": "progress",
                    "data": json.dumps(
                        {
                            "type": "progress",
                            "status": "running",
                            "data": {
                                "stage": "outline_done",
                                "message": f"大纲: {outline.get('title', '')}",
                                "outline": outline,
                            },
                        }
                    ),
                }
                last_update_hash = "running:outline_done:0"

            while True:
                status_info = task_status.get(history_id)

                if not status_info:
                    no_task_count += 1
                    db.refresh(history)
                    if history.status == "completed":
                        yield {
                            "event": "done",
                            "data": json.dumps(
                                {
                                    "type": "done",
                                    "status": "completed",
                                    "data": {
                                        "stage": "done",
                                        "message": "生成完成",
                                        "book_id": history.book_id,
                                        "book_title": history.outline.get("title", "未命名电子书") if history.outline else "未命名电子书",
                                    },
                                }
                            ),
                        }
                        break
                    elif history.status == "failed":
                        yield {
                            "event": "error",
                            "data": json.dumps(
                                {
                                    "type": "error",
                                    "status": "failed",
                                    "data": {
                                        "stage": "error",
                                        "message": history.error_message or "未知错误",
                                    },
                                }
                            ),
                        }
                        break
                    elif no_task_count >= max_no_task_wait:
                        yield {
                            "event": "error",
                            "data": json.dumps(
                                {
                                    "type": "error",
                                    "status": "failed",
                                    "data": {
                                        "stage": "error",
                                        "message": "任务状态丢失，请刷新页面重试",
                                    },
                                }
                            ),
                        }
                        break
                    else:
                        await asyncio.sleep(0.5)
                        continue
                else:
                    no_task_count = 0

                current_status = status_info["status"]
                progress = status_info["progress"]

                update_hash = f"{current_status}:{progress.get('stage')}:{progress.get('current_chapter', 0)}"

                if update_hash != last_update_hash:
                    yield {
                        "event": "progress",
                        "data": json.dumps(
                            {
                                "type": "progress",
                                "status": current_status,
                                "data": progress,
                            }
                        ),
                    }
                    last_update_hash = update_hash

                if current_status in ("completed", "failed", "cancelled"):
                    final_event = "done" if current_status == "completed" else "error"
                    yield {
                        "event": final_event,
                        "data": json.dumps({"type": final_event, "data": progress}),
                    }
                    break

                await asyncio.sleep(0.3)

        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())


@router.post("/{history_id}/cancel")
async def cancel_generation(history_id: int, db: Session = Depends(get_db)):
    history = (
        db.query(GenerationHistory).filter(GenerationHistory.id == history_id).first()
    )
    if not history:
        raise HTTPException(status_code=404, detail="History not found")

    if history.status == "pending" and history_id in task_status:
        # 设置取消标志
        task_status[history_id]["cancelled"] = True

        # 更新数据库状态
        history.status = "deleted"
        db.commit()

        return {"message": "Cancellation requested"}

    return {"message": "Generation not active"}


@router.get("/history")
def get_history(status: str = None, db: Session = Depends(get_db)):
    user_id = generate_user_id()
    query = db.query(GenerationHistory).filter(GenerationHistory.author_id == user_id)

    if status and status != "all":
        query = query.filter(GenerationHistory.status == status)

    return query.order_by(GenerationHistory.created_at.desc()).all()


@router.get("/history/{history_id}")
def get_history_detail(history_id: int, db: Session = Depends(get_db)):
    history = (
        db.query(GenerationHistory).filter(GenerationHistory.id == history_id).first()
    )
    if not history:
        raise HTTPException(status_code=404, detail="History not found")

    # 附加内存中的任务状态
    result = {
        "id": history.id,
        "prompt": history.prompt,
        "requirements": history.requirements,
        "outline": history.outline,
        "status": history.status,
        "error_message": history.error_message,
        "created_at": history.created_at,
        "completed_at": history.completed_at,
        "author_id": history.author_id,
        "book_id": history.book_id,
        "language": history.language,
        "task_status": task_status.get(history_id),
    }
    return result


@router.post("/history/{history_id}/cancel")
def cancel_history(history_id: int, db: Session = Depends(get_db)):
    """取消进行中的生成任务，标记为已删除"""
    history = (
        db.query(GenerationHistory).filter(GenerationHistory.id == history_id).first()
    )
    if not history:
        raise HTTPException(status_code=404, detail="History not found")

    if history.status == "pending" and history_id in task_status:
        task_status[history_id]["cancelled"] = True

    history.status = "deleted"
    db.commit()

    return {"message": "History cancelled"}


@router.delete("/history/{history_id}/permanent")
def delete_history_permanent(history_id: int, db: Session = Depends(get_db)):
    """永久删除历史记录"""
    history = (
        db.query(GenerationHistory).filter(GenerationHistory.id == history_id).first()
    )
    if not history:
        raise HTTPException(status_code=404, detail="History not found")

    # 如果任务还在运行，先取消
    if history.status == "pending" and history_id in task_status:
        task_status[history_id]["cancelled"] = True
        del task_status[history_id]

    db.delete(history)
    db.commit()

    return {"message": "History permanently deleted"}


@router.delete("/history/clear-deleted")
def clear_deleted_history(db: Session = Depends(get_db)):
    """清空所有已删除的历史记录"""
    user_id = generate_user_id()
    deleted = (
        db.query(GenerationHistory)
        .filter(
            GenerationHistory.author_id == user_id,
            GenerationHistory.status == "deleted",
        )
        .all()
    )

    count = 0
    for h in deleted:
        if h.id in task_status:
            del task_status[h.id]
        db.delete(h)
        count += 1

    db.commit()
    return {"message": f"Cleared {count} deleted records"}
