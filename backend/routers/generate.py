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
    enable_meaning: bool = False  # Plan 生成意图表(Meaning Table)，Route/Execute 可向 Plan 咨询


def _load_card(card_id: str | None):
    if not card_id:
        return None
    from models import WritingCard

    db = SessionLocal()
    try:
        return db.query(WritingCard).filter(WritingCard.id == card_id).first()
    finally:
        db.close()


def _maybe_consult_plan(plan_agent, index, chapter, language, provider_id, model_name) -> str:
    """Execute 层：本章线程先思考「是否需要向 Plan 提问详细意图」，需要才咨询（只读）。

    返回要注入写作 prompt 的意图说明（可能为空）。绝不修改意图表。
    """
    from services.llm_service import get_llm_service

    # 先让本章自评是否需要咨询（一次轻量判断）
    try:
        svc = get_llm_service(provider_id, model_name)
        judge_sys = (
            "你即将撰写某一章，但拿不准它在全书中的确切意图/前后衔接时，可以向总规划者(Plan)咨询。"
            '只输出 JSON：{"ask": true/false, "question": "若 ask=true，给出你想问 Plan 的具体问题"}。'
            "仅当确有不确定时才 ask=true。"
        )
        judge_user = f"章节{index + 1}：{chapter.get('title','')}\n概要：{chapter.get('summary','')}"
        raw = svc.generate_sync(judge_sys, judge_user, max_tokens=300)
        import json as _json, re as _re
        m = _re.search(r"\{[\s\S]*\}", raw or "")
        decision = _json.loads(m.group(0)) if m else {}
    except Exception:
        decision = {}

    if not decision.get("ask"):
        # 不主动提问也注入一份本章意图切片（来自 Plan 的只读表），让写作贴合规划
        return plan_agent.chapter_intent_note(index)

    res = plan_agent.consult(
        asker=f"第{index + 1}章",
        question=decision.get("question", "本章的确切意图与前后衔接是什么？"),
        locator={"scope": "chapter", "index": index},
        allow_modify=False,  # Execute 只读，不改意图表
    )
    note = plan_agent.chapter_intent_note(index)
    reply = (res.get("reply") or "").strip()
    if reply:
        note = (note + f"\n【Plan 答复】{reply}").strip()
    return note


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
    enable_meaning: bool = False,
    resume: bool = False,
):
    """在后台线程中运行生成任务。

    resume=True 时为断点续传：复用已持久化的大纲、跳过已落库的章节、
    恢复 stub/意图表快照，只补跑缺失的章节。
    """
    import threading
    from services.llm_service import generate_outline_sync, generate_chapter_sync, get_llm_service
    from services.book_builder import save_book_sync
    from services.checkpoint import (
        save_chapter_draft, load_chapter_drafts, clear_chapter_drafts,
        save_resume_state, load_resume_state,
    )

    db = SessionLocal()
    try:
        # 断点续传：预载已完成的章节草稿 + 跨章状态快照
        resumed_drafts = load_chapter_drafts(history_id) if resume else {}
        resume_blob = load_resume_state(history_id) if resume else {}
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

        # 续传：若已有持久化大纲则直接复用，跳过昂贵的大纲生成
        existing_row = db.query(GenerationHistory).filter(
            GenerationHistory.id == history_id
        ).first()
        outline = existing_row.outline if (resume and existing_row and existing_row.outline) else None

        if outline is None:
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

        # ---- Plan 阶段：生成 Meaning Table（意图表），Plan 独占其写权限 ----
        plan_agent = None
        if enable_meaning:
            from services.plan_agent import PlanAgent
            plan_agent = PlanAgent(provider_id, model_name, language)
            if resume and resume_blob.get("plan"):
                # 续传：从快照恢复意图表，不再调 LLM 重建
                tbl = plan_agent.restore(resume_blob["plan"], resume_blob.get("plan_version", 0))
                msg = "意图表已从续传快照恢复"
            else:
                tbl = plan_agent.build(outline, prompt, requirements)
                msg = "意图表已生成（全书 + 各章意图与前后衔接）" if tbl else "意图表生成失败，按普通流程继续"
            task_status[history_id]["progress"] = {
                "stage": "meaning",
                "message": msg,
                "total_chapters": len(outline["chapters"]),
                "outline": outline,
            }

        # ---- Plan → Route → Execute 三层：Route 产出调度表，Execute 照表执行 ----
        from services.stub_service import StubStore
        from services.chapter_router import plan_schedule, describe_schedule
        from services.agent_tools import web_search_configured

        stub_store = StubStore()          # 线程安全的 stub 仓库（读写过锁）
        if enable_stub and resume and resume_blob.get("stubs"):
            stub_store.restore(resume_blob["stubs"])   # 续传：恢复 stub 待办
        total_chapters = len(outline["chapters"])
        # 续传：预载已完成章节，schedule 执行时会跳过它们
        chapter_results = {i: c for i, c in resumed_drafts.items() if 0 <= i < total_chapters}
        done_count = {"n": len(chapter_results)}
        progress_lock = threading.Lock()

        # Route 层：判定章节耦合度，产出调度表（哪些串行、哪些并行）
        # Route 携带意图表，并可带疑问 + 定位向 Plan 咨询（Plan 可能据此修订意图表）
        def _on_plan(ev):
            task_status[history_id]["progress"] = {
                "stage": "plan_consult",
                "message": f"[{ev.get('asker')}→Plan] {ev.get('reply','')[:160]}" + ("（已修订意图表）" if ev.get("modified") else ""),
                "total_chapters": len(outline["chapters"]),
                "outline": outline,
            }

        schedule = plan_schedule(
            outline, provider_id, model_name, enabled=enable_concurrency,
            plan_agent=plan_agent, on_plan=_on_plan,
        )
        task_status[history_id]["progress"] = {
            "stage": "route",
            "message": "调度计划：" + describe_schedule(schedule),
            "schedule": schedule,
            "total_chapters": total_chapters,
            "outline": outline,
        }

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

            # Execute → Plan 咨询：本章线程自行决定「是否向 Plan 提问详细意图」（只读，不改意图表）
            if plan_agent is not None and plan_agent.ready:
                try:
                    note = _maybe_consult_plan(plan_agent, i, chapter, language, provider_id, model_name)
                    if note:
                        merged_card_context = (merged_card_context + "\n\n" + note).strip()
                        with progress_lock:
                            task_status[history_id]["progress"] = {
                                "stage": "plan_consult",
                                "message": f"[第{i+1}章→Plan] 已获取意图澄清",
                                "current_chapter": done_count["n"],
                                "total_chapters": total_chapters,
                                "outline": outline,
                            }
                except Exception as e:
                    print(f"[Plan] execute consult failed (ch{i}): {e}")

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

        # Execute 层：照调度表从上到下执行。serial 步顺序写；parallel 步并发写。
        # 每写完一章立即落库（checkpoint）；barrier 后存一次 stub/意图表快照。
        def _persist_state():
            save_resume_state(history_id, stub_store if enable_stub else None, plan_agent)

        max_workers = max(1, min(int(max_concurrency or 1), 4))
        for step in schedule:
            if _cancelled():
                db.query(GenerationHistory).filter(GenerationHistory.id == history_id).update({"status": "deleted"})
                db.commit()
                task_status[history_id]["status"] = "cancelled"
                return
            # 续传：本步中已完成的章直接跳过，只跑缺失的
            pending = [idx for idx in step["chapters"] if idx not in chapter_results]
            if not pending:
                continue
            if step["mode"] == "parallel" and len(pending) > 1 and max_workers > 1:
                from concurrent.futures import ThreadPoolExecutor, as_completed
                # 冻结意图表 + stub 仓库：并发期间所有章节读到同一份「步前快照」，
                # 各自的写操作（改意图表 / 登记兑现 stub）排队，待本步结束的 barrier 单线程统一提交。
                # 这样消除"某章中途改写、其它章节正在跑"导致的 stale read 时序不确定。
                if plan_agent is not None and plan_agent.ready:
                    plan_agent.freeze()
                if enable_stub:
                    stub_store.freeze()
                try:
                    with ThreadPoolExecutor(max_workers=max_workers) as pool:
                        futs = {pool.submit(_gen_one_chapter, idx, outline["chapters"][idx]): idx for idx in pending}
                        for fut in as_completed(futs):
                            idx = futs[fut]
                            content = fut.result()
                            chapter_results[idx] = content
                            save_chapter_draft(history_id, idx, content)  # 每章完成即落库
                finally:
                    # barrier：本步章节全部结束，此刻单线程，统一提交缓冲的写操作 → 下一步可见
                    if enable_stub:
                        stub_store.unfreeze()
                    if plan_agent is not None and plan_agent.ready:
                        if plan_agent.unfreeze():
                            task_status[history_id]["progress"] = {
                                "stage": "plan_consult",
                                "message": f"[barrier] 意图表已在并发步结束后更新（v{plan_agent.version()}）",
                                "total_chapters": total_chapters,
                                "outline": outline,
                            }
                _persist_state()  # barrier 后：stub/意图表已提交，存快照
            else:
                # 串行步：单线程，改表立即生效，下一章天然读到最新（无陈旧读）
                for idx in pending:
                    if _cancelled():
                        break
                    content = _gen_one_chapter(idx, outline["chapters"][idx])
                    chapter_results[idx] = content
                    save_chapter_draft(history_id, idx, content)  # 每章完成即落库
                    _persist_state()

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

        # 成功成书后清理中间草稿 checkpoint
        clear_chapter_drafts(history_id)

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

    # 断点续传：存下全部生成参数，续传时据此原样重启
    gen_params = {
        "provider_id": request.provider_id,
        "model_name": request.model_name,
        "card_id": request.card_id,
        "extra_requirements": request.extra_requirements,
        "tags": request.tags,
        "enable_research": request.enable_research,
        "enable_rich": request.enable_rich,
        "enable_stub": request.enable_stub,
        "enable_concurrency": request.enable_concurrency,
        "max_concurrency": request.max_concurrency,
        "enable_meaning": request.enable_meaning,
    }

    # 创建历史记录
    history = GenerationHistory(
        prompt=request.prompt,
        requirements=request.requirements,
        status="pending",
        author_id=user_id,
        language=language,
        gen_params=gen_params,
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
        request.enable_meaning,
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


@router.post("/{history_id}/resume")
async def resume_generation(history_id: int, db: Session = Depends(get_db)):
    """断点续传：对崩溃/失败/中断的任务，复用已落库的章节，只补跑缺失的部分。"""
    history = (
        db.query(GenerationHistory).filter(GenerationHistory.id == history_id).first()
    )
    if not history:
        raise HTTPException(status_code=404, detail="History not found")

    # 已完成的无需续传
    if history.status == "completed" and history.book_id:
        return {"message": "already completed", "history_id": history_id, "book_id": history.book_id}

    # 正在跑的不重复启动
    cur = task_status.get(history_id)
    if cur and cur.get("status") in ("running", "starting"):
        return {"message": "already running", "history_id": history_id}

    params = history.gen_params or {}

    from services.checkpoint import load_chapter_drafts
    done = load_chapter_drafts(history_id)

    # 复位状态为 pending，供取消检查等逻辑正常工作
    history.status = "pending"
    history.error_message = None
    db.commit()

    task_status[history_id] = {
        "status": "starting",
        "progress": {"stage": "starting", "message": f"续传中：已完成 {len(done)} 章，补跑其余..."},
        "cancelled": False,
    }

    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        executor,
        run_generation_task,
        history_id,
        history.prompt,
        history.requirements or {},
        history.author_id,
        history.language or "zh-CN",
        params.get("provider_id"),
        params.get("model_name"),
        params.get("card_id"),
        params.get("extra_requirements", ""),
        params.get("tags", []),
        params.get("enable_research", False),
        params.get("enable_rich", True),
        params.get("enable_stub", False),
        params.get("enable_concurrency", False),
        params.get("max_concurrency", 3),
        params.get("enable_meaning", False),
        True,  # resume
    )
    return {"message": "resumed", "history_id": history_id, "resumed_chapters": len(done)}


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
