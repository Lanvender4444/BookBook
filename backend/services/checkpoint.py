"""断点续传（checkpoint / resume）持久化。

生成一本书是长任务：以前各章内容只存在内存里，`chapter_results` 攒到最后才由
`save_book_sync` 一次性落盘。这带来一个真实缺陷——任务进行到一半崩溃/卡死/进程被杀，
所有已写好的章节全部丢失，只能从头再来。

本模块把"每写完一章"变成一次持久化的 checkpoint：
  · save_chapter_draft：一章写完立即 upsert 到 chapter_drafts 表（各线程各自的 session）；
  · load_chapter_drafts：续传时取回已完成的章 → 直接跳过，不重跑；
  · save_resume_state / load_resume_state：把 stub 仓库 + 意图表快照存进 generation_history，
    续传时恢复跨章状态（stub 待办、Meaning Table），保证续写的章仍能看到前文登记的 stub 与意图。

写入用 SQLite（WAL 模式，见 database.py）。多章线程并发落 checkpoint 时，SQLite 以行级/库级
写锁串行化写入（busy_timeout 让竞争者等待而非报错），每个线程只写自己那一章的行（chapter_index
互不相同），因此不会互相覆盖，也无需应用层再加锁。
"""

from models import ChapterDraft, GenerationHistory


def save_chapter_draft(history_id: int, chapter_index: int, content: str) -> None:
    """一章写完立即落库（upsert）。用独立 session，可被任意工作线程安全调用。"""
    from database import SessionLocal

    db = SessionLocal()
    try:
        row = (
            db.query(ChapterDraft)
            .filter(
                ChapterDraft.history_id == history_id,
                ChapterDraft.chapter_index == chapter_index,
            )
            .first()
        )
        if row:
            row.content = content
        else:
            db.add(
                ChapterDraft(
                    history_id=history_id,
                    chapter_index=chapter_index,
                    content=content,
                )
            )
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[checkpoint] save draft failed (h{history_id} c{chapter_index}): {e}")
    finally:
        db.close()


def load_chapter_drafts(history_id: int) -> dict:
    """取回该任务已落库的章节草稿：{chapter_index: content}。"""
    from database import SessionLocal

    db = SessionLocal()
    try:
        rows = (
            db.query(ChapterDraft)
            .filter(ChapterDraft.history_id == history_id)
            .all()
        )
        return {r.chapter_index: (r.content or "") for r in rows}
    except Exception as e:
        print(f"[checkpoint] load drafts failed (h{history_id}): {e}")
        return {}
    finally:
        db.close()


def clear_chapter_drafts(history_id: int) -> None:
    """任务成功完成、正式落盘成书后，清理该任务的中间草稿。"""
    from database import SessionLocal

    db = SessionLocal()
    try:
        db.query(ChapterDraft).filter(ChapterDraft.history_id == history_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[checkpoint] clear drafts failed (h{history_id}): {e}")
    finally:
        db.close()


def save_resume_state(history_id: int, stub_store=None, plan_agent=None) -> None:
    """把跨章状态（stub 待办 + 意图表快照 + 版本号）存进 generation_history。

    在 barrier / 每章完成后调用（单线程时刻），供续传恢复。
    """
    from database import SessionLocal

    state = {}
    try:
        if stub_store is not None:
            state["stubs"] = stub_store.snapshot()
        if plan_agent is not None and getattr(plan_agent, "ready", False):
            state["plan"] = plan_agent.snapshot()
            state["plan_version"] = plan_agent.version()
    except Exception as e:
        print(f"[checkpoint] snapshot resume_state failed (h{history_id}): {e}")
        return

    db = SessionLocal()
    try:
        db.query(GenerationHistory).filter(
            GenerationHistory.id == history_id
        ).update({"resume_state": state})
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[checkpoint] save resume_state failed (h{history_id}): {e}")
    finally:
        db.close()


def load_resume_state(history_id: int) -> dict:
    from database import SessionLocal

    db = SessionLocal()
    try:
        h = (
            db.query(GenerationHistory)
            .filter(GenerationHistory.id == history_id)
            .first()
        )
        return (h.resume_state if h and h.resume_state else {}) or {}
    finally:
        db.close()
