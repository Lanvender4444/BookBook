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
    enable_research: bool = False  # 开启 ReAct 研究循环（每章决定是否 web 搜索 / 查知识库）
    enable_rich: bool = True  # 写作时内容工具：允许模型在正文插入表格 / SVG 图
    enable_stub: bool = False  # 跨章占位 Stub：前向引用与自动跳转链接
    enable_concurrency: bool = False  # 章节并发：路由分析依赖后并行生成无依赖章节
    max_concurrency: int = 3  # 并发上限（避免触发 LLM 限流）


def _load_card(card_id: str | None):
    if not card_id:
        return None
    from models import WritingCard

    db = SessionLocal()
    try:
        return db.query(WritingCard).filter(WritingCard.id == card_id).first()
    finally:
        db.close()


def _card_source_ids(card) -> list:
    """写作卡关联的全部知识源 id（供 ReAct 的 search_knowledge 工具检索）。"""
    if card is None:
        return []
    ids = []
    for field in ("writing_guide_ids", "style_ids", "reference_ids", "continuation_ids"):
        ids.extend(getattr(card, field, None) or [])
    return list(dict.fromkeys(ids))


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
    enable_research: bool = False,
    enable_rich: bool = True,
    enable_stub: bool = False,
    enable_concurrency: bool = False,
    max_concurrency: int = 3,
):
    """在后台线程中运行生成任务"""
    import threading
    from services.llm_service import generate_outline_sync, generate_chapter_sync, get_llm_service
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

        # ---- Plan-and-Execute：路由分析并发波，再逐波执行（每章独立 ReAct） ----
        from services.stub_service import StubStore
        from services.chapter_router import plan_waves
        from services.agent_tools import web_search_configured

        stub_store = StubStore()          # 线程安全的 stub 仓库（读写过锁）
        total_chapters = len(outline["chapters"])
        chapter_results = {}              # {index: content}
        done_count = {"n": 0}
        progress_lock = threading.Lock()

        # 路由：哪些章节可以并发
        waves = plan_waves(outline, provider_id, model_name, enabled=enable_concurrency)

        def _cancelled():
            return task_status.get(history_id, {}).get("cancelled")

        def _gen_one_chapter(i: int, chapter: dict) -> str:
            """单章执行：(可选) ReAct 研究 → 写作 → stub 处理 → 内容工具。线程内运行。"""
            with progress_lock:
                task_status[history_id]["progress"] = {
                    "stage": "chapter",
                    "message": f"正在生成第 {i + 1}/{total_chapters} 章: {chapter.get('title', '')}",
                    "current_chapter": done_count["n"],
                    "total_chapters": total_chapters,
                    "chapter_title": chapter.get("title", ""),
                    "outline": outline,
                }

            chapter_query = f"{chapter.get('title', '')} {chapter.get('summary', '')}".strip() or prompt
            chapter_ctx = _card_context_for(card, chapter_query, extra_requirements)

            # 每章独立的 ReAct 研究循环
            research_notes = ""
            if enable_research:
                try:
                    from services.react_agent import research_chapter

                    def _on_research(ev):
                        with progress_lock:
                            task_status[history_id]["progress"] = {
                                "stage": "research",
                                "message": ev.get("message", ""),
                                "research_stage": ev.get("stage"),
                                "tool": ev.get("tool"),
                                "current_chapter": done_count["n"],
                                "total_chapters": total_chapters,
                                "chapter_title": chapter.get("title", ""),
                                "outline": outline,
                            }

                    svc = get_llm_service(provider_id, model_name)
                    research_notes = research_chapter(
                        svc, outline, chapter, i,
                        language_name=language,
                        source_ids=_card_source_ids(card),
                        web_available=web_search_configured(),
                        knowledge_available=bool(_card_source_ids(card)),
                        on_event=_on_research,
                    )
                except Exception as e:
                    print(f"[ReAct] research failed (ch{i}): {e}")

            merged_card_context = chapter_ctx["card_context"]
            if research_notes:
                merged_card_context = (merged_card_context + "\n\n" + research_notes).strip()

            # stub 待办（加锁快照）注入 prompt
            stub_note = stub_store.prompt() if enable_stub else ""

            content = generate_chapter_sync(
                outline, chapter, i,
                provider_id=provider_id, model_name=model_name, language=language,
                card_context=merged_card_context,
                extra_requirements=chapter_ctx["extra_requirements"],
                has_continuation=chapter_ctx["has_continuation"],
                enable_rich=enable_rich,
                stub_note=stub_note,
                post_process=not enable_stub,  # 开 stub 时延迟 content_tools
            )

            if enable_stub:
                content = stub_store.process(content, i)   # 登记/兑现，过锁
                if enable_rich:
                    from services.content_tools import apply_content_tools
                    content = apply_content_tools(content)

            with progress_lock:
                done_count["n"] += 1
                task_status[history_id]["progress"] = {
                    "stage": "chapter_done",
                    "message": f"第 {i + 1} 章完成（{done_count['n']}/{total_chapters}）",
                    "current_chapter": done_count["n"],
                    "total_chapters": total_chapters,
                    "chapter_title": chapter.get("title", ""),
                    "chapter_content": content,
                }
            return content

        # 逐波执行：波内并发，波间串行（后波可见前波登记的 stub）
        max_workers = max(1, min(int(max_concurrency or 1), 4)) if enable_concurrency else 1
        for wave in waves:
            if _cancelled():
                db.query(GenerationHistory).filter(GenerationHistory.id == history_id).update({"status": "deleted"})
                db.commit()
                task_status[history_id]["status"] = "cancelled"
                return
            if max_workers > 1 and len(wave) > 1:
                from concurrent.futures import ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=max_workers) as pool:
                    futs = {idx: pool.submit(_gen_one_chapter, idx, outline["chapters"][idx]) for idx in wave}
                    for idx, fut in futs.items():
                        chapter_results[idx] = fut.result()
            else:
                for idx in wave:
                    if _cancelled():
                        break
                    chapter_results[idx] = _gen_one_chapter(idx, outline["chapters"][idx])

        if _cancelled():
            db.query(GenerationHistory).filter(GenerationHistory.id == history_id).update({"status": "deleted"})
            db.commit()
            task_status[history_id]["status"] = "cancelled"
            return

        # 按章节顺序组装
        chapters = [chapter_results.get(i, "") for i in range(total_chapters)]

        # 缝合跨章 stub：已兑现的在源处加跳转链接，未兑现的清理锚点
        if enable_stub:
            stub_store.stitch(chapters)

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
        request.enable_research,
        request.enable_rich,
        request.enable_stub,
        request.enable_concurrency,
        request.max_concurrency,
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
