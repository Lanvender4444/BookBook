"""Route 层：章节调度器（Plan → Route → Execute 三层架构的中间层）。

职责：大纲（Plan 产物）生成后，Route 层独立判定章节之间的「耦合程度」，
产出一张**调度表(schedule)**交给 Execute 层照表执行。

调度表是一个有序的「执行步骤」列表，每一步标注串行还是并行：
    [
      {"mode": "serial",   "chapters": [0]},        # 单章串行
      {"mode": "parallel", "chapters": [1, 2, 3]},  # 这几章彼此关系不大，可并行
      {"mode": "serial",   "chapters": [4]},
      ...
    ]
Execute 层从上到下执行：serial 步顺序写其中的章节；parallel 步把其中章节并发写。

判定原则（交给 LLM，它最懂内容衔接）：
- 紧耦合（前后直接延续/总结/回指/共享伏笔）→ 必须串行，且按编号先后；
- 松耦合（各讲各的主题、彼此独立）→ 可并行成组。
解析失败一律降级为「全串行」（每章一个 serial 步），保证安全。
"""

import json
import re


def _extract_json(text: str):
    m = re.search(r"\{[\s\S]*\}", text or "")
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def sequential_schedule(n: int) -> list:
    """降级方案：每章一个串行步，完全串行。"""
    return [{"mode": "serial", "chapters": [i]} for i in range(n)]


def _normalize_schedule(steps_raw, n: int) -> list:
    """校验并规整 LLM 给的调度表：保证每章恰好出现一次、编号合法、并行步去重。

    任何不合法（缺章/重复/越界）→ 返回 None，由调用方降级。
    """
    if not isinstance(steps_raw, list) or not steps_raw:
        return None
    schedule = []
    seen = set()
    for step in steps_raw:
        if not isinstance(step, dict):
            return None
        chapters = step.get("chapters", [])
        if not isinstance(chapters, list):
            return None
        ids = []
        for c in chapters:
            try:
                ci = int(c)
            except (TypeError, ValueError):
                return None
            if ci < 0 or ci >= n or ci in seen:
                return None
            seen.add(ci)
            ids.append(ci)
        if not ids:
            continue
        mode = "parallel" if str(step.get("mode", "")).lower().startswith("p") and len(ids) > 1 else "serial"
        # 串行步若含多章，拆成多个串行步，保持「串行即按序逐章」语义
        if mode == "serial" and len(ids) > 1:
            for ci in sorted(ids):
                schedule.append({"mode": "serial", "chapters": [ci]})
        else:
            schedule.append({"mode": mode, "chapters": ids})
    if seen != set(range(n)):
        return None  # 必须覆盖且仅覆盖所有章节
    return schedule


def plan_schedule(outline: dict, provider_id: str = None, model_name: str = None, enabled: bool = True,
                  plan_agent=None, on_plan=None) -> list:
    """Route 层入口：返回调度表 list[{"mode","chapters"}]。

    enabled=False（用户未开并发）或任何失败 → 全串行调度表。
    plan_agent 不为空时，Route 会带着「并发是否破坏意图衔接」的疑问向 Plan 咨询，
    Plan 可据此修订意图表（写权限仍只在 Plan），并把建议反馈给 Route 影响调度。
    """
    chapters = outline.get("chapters", []) or []
    n = len(chapters)
    if n == 0:
        return []
    if not enabled or n == 1:
        return sequential_schedule(n)

    try:
        from services.llm_service import get_llm_service

        service = get_llm_service(provider_id, model_name)
        ch_list = "\n".join(
            f'{i}. {c.get("title","")}：{c.get("summary","")}' for i, c in enumerate(chapters)
        )

        # Route → Plan 咨询：带着调度疑问 + 全书定位，问 Plan 哪些章节意图上强绑定不宜并行
        plan_advice = ""
        if plan_agent is not None and getattr(plan_agent, "ready", False):
            try:
                res = plan_agent.consult(
                    asker="Route(调度器)",
                    question="从全书意图与前后衔接看，哪些章节意图上强绑定、必须串行（不宜并行）？请给出建议。",
                    locator={"scope": "book"},
                    allow_modify=True,   # Route 咨询允许 Plan 修订意图表
                    on_event=on_plan,
                )
                plan_advice = (res.get("reply") or "").strip()
            except Exception as e:
                print(f"[route] plan consult failed: {e}")
        system_prompt = (
            "你是书籍生成流水线的【调度器】。给定章节列表，判断每章之间的耦合程度，"
            "产出一张调度表，决定哪些章节必须串行、哪些关系不大可以并行。\n"
            "判定原则：\n"
            "- 紧耦合（后一章直接延续/总结/回指前一章，或共享需先建立的设定/伏笔）→ 必须串行，按编号先后；\n"
            "- 松耦合（各讲独立主题、互不依赖）→ 可并行成组。\n"
            "- 并行组里的章节必须彼此独立；拿不准就归为串行，保证连贯性。\n\n"
            "只输出 JSON（不要解释），格式：\n"
            '{"schedule": [{"mode":"serial","chapters":[0]}, {"mode":"parallel","chapters":[1,2]}, {"mode":"serial","chapters":[3]}]}\n'
            "要求：每个章节编号恰好出现一次，覆盖 0.."
            + str(n - 1)
            + "，顺序大体遵循叙事推进。"
        )
        advice_block = f"\n\n总规划者(Plan)对串行/并行的建议（请优先采纳）：\n{plan_advice}" if plan_advice else ""
        user_message = f"章节列表：\n{ch_list}{advice_block}\n\n请输出调度表 JSON。"
        raw = service.generate_sync(system_prompt, user_message, max_tokens=900)
        data = _extract_json(raw) or {}
        schedule = _normalize_schedule(data.get("schedule"), n)
        if schedule is None:
            print("[route] schedule invalid, fallback sequential")
            return sequential_schedule(n)
        return schedule
    except Exception as e:
        print(f"[route] plan_schedule failed, fallback sequential: {e}")
        return sequential_schedule(n)


def describe_schedule(schedule: list) -> str:
    """把调度表渲染成给前端展示的简短描述。"""
    parts = []
    for step in schedule:
        chs = step["chapters"]
        if step["mode"] == "parallel" and len(chs) > 1:
            parts.append("并行[" + "+".join(f"第{c+1}章" for c in chs) + "]")
        else:
            parts.append(f"第{chs[0]+1}章")
    return " → ".join(parts)
