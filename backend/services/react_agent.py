"""每章生成的 ReAct（Reason + Act）循环。

流程：在正式写每一章之前，先让模型做若干轮「思考 → 决定是否用工具 → 观察结果」，
把收集到的资料作为研究笔记，再把笔记注入正式的写章 prompt。

实现要点：
- 不依赖各家厂商的原生 function calling，改用「文本 JSON 行动协议」，
  只用现有的 generate_sync(system, user) 接口即可，所有 provider 通用。
- 每轮模型必须输出一个 JSON：
    {"thought": "...", "action": "web_search|search_knowledge|finish", "query": "..."}
  action=finish 表示资料够了，结束研究。
- on_event 回调用于把思考/工具调用过程实时推给前端进度。
"""

import json
import re

from services.agent_tools import run_tool, tools_spec

MAX_STEPS = 4  # 每章最多调用工具的轮数，防止无限循环 / 烧 token


def _extract_json(text: str) -> dict | None:
    """从模型输出里抽第一个 JSON 对象。"""
    # 优先 ```json ``` 代码块
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    raw = m.group(1) if m else None
    if raw is None:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            raw = text[start : end + 1]
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # 容错：截到第一个平衡的花括号
        try:
            depth = 0
            for i, ch in enumerate(raw):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return json.loads(raw[: i + 1])
        except Exception:
            return None
    return None


def research_chapter(
    service,
    outline: dict,
    chapter: dict,
    chapter_index: int,
    language_name: str,
    source_ids: list[str],
    web_available: bool,
    knowledge_available: bool,
    on_event=None,
    papers_available: bool = True,
) -> str:
    """对单章执行 ReAct 研究循环，返回「研究笔记」文本（供写章时注入）。

    若模型一上来就判断无需工具，返回空字符串（不影响正常写作）。
    """
    if not web_available and not knowledge_available and not papers_available:
        return ""

    def emit(payload):
        if on_event:
            try:
                on_event(payload)
            except Exception:
                pass

    spec = tools_spec(knowledge_available, web_available, papers_available)
    system_prompt = f"""你是一个严谨的写作研究助手，正在为书籍《{outline.get('title', '')}》的某一章做资料准备。
你的任务不是写作，而是判断：写好这一章是否需要查资料？如果需要，用工具查；如果本章是常识/虚构创作不需要外部资料，就直接结束。

可用工具：
{spec}

每一步你必须只输出一个 JSON 对象，不要输出别的内容，格式：
{{"thought": "你的简短思考（{language_name}）", "action": "web_search / search_papers / search_knowledge / finish", "query": "当 action 是工具时的检索词；finish 时留空"}}

规则：
1. 优先判断本章是否真的需要外部资料。纯虚构小说情节、常识性内容通常不需要，直接 action=finish。
2. 需要最新事实/数据用 web_search；需要严谨学术依据用 search_papers；需要用户提供的资料/风格/续写原文用 search_knowledge。
3. 最多查 {MAX_STEPS} 次。资料足够后必须 action=finish。"""

    history = [
        f"章节标题：{chapter.get('title', '')}",
        f"章节概要：{chapter.get('summary', '')}",
        "请开始判断与研究。",
    ]
    notes = []

    for step in range(MAX_STEPS):
        user_message = "\n".join(history) + "\n\n请输出本步的 JSON 决策。"
        try:
            raw = service.generate_sync(system_prompt, user_message, max_tokens=600)
        except Exception as e:
            emit({"type": "research", "stage": "error", "message": f"研究步骤失败: {e}"})
            break

        decision = _extract_json(raw) or {}
        action = (decision.get("action") or "").strip()
        thought = (decision.get("thought") or "").strip()
        query = (decision.get("query") or "").strip()

        if thought:
            emit({"type": "research", "stage": "thought", "message": thought, "step": step + 1})

        if action in ("finish", "", "none", "stop") or (action not in ("web_search", "search_papers", "search_knowledge")):
            break

        emit({"type": "research", "stage": "tool", "tool": action, "query": query, "step": step + 1})
        observation = run_tool(action, query, source_ids)
        emit({"type": "research", "stage": "observation", "tool": action, "message": observation[:300]})

        notes.append(f"【{action}: {query}】\n{observation}")
        history.append(f"你执行了 {action}（{query}），观察结果：\n{observation}\n请基于此继续判断是否还需查资料。")

    if not notes:
        return ""
    return "# 研究笔记（写作时请参考并核实，用本书语言表达）\n\n" + "\n\n".join(notes)
