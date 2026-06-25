"""章节路由 / 并发调度器。

Plan-and-Execute 架构里的「路由管理」：大纲生成后，分析章节之间的依赖关系，
把章节分成若干「并发波(wave)」——同一波内的章节互不依赖，可并发生成；
波与波之间串行（后一波可能依赖前一波）。

依赖判断由 LLM 完成（它最懂内容衔接）；解析/拓扑失败时一律降级为全串行（每章一波），保证安全。
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


def _sequential_waves(n: int):
    """降级方案：每章单独一波，完全串行。"""
    return [[i] for i in range(n)]


def _topo_waves(n: int, deps: dict) -> list:
    """按依赖做分层拓扑排序，输出并发波。出现环或非法依赖则降级串行。"""
    # 规整依赖：只接受 0..n-1 且 j < i（只能依赖前文，避免环与时间悖论）
    clean = {i: set() for i in range(n)}
    for i in range(n):
        for j in deps.get(i, []):
            if isinstance(j, int) and 0 <= j < n and j != i:
                clean[i].add(j)
    waves, placed = [], set()
    guard = 0
    while len(placed) < n and guard <= n:
        guard += 1
        wave = [i for i in range(n) if i not in placed and clean[i] <= placed]
        if not wave:
            return _sequential_waves(n)  # 有环 → 降级
        waves.append(sorted(wave))
        placed.update(wave)
    return waves if len(placed) == n else _sequential_waves(n)


def plan_waves(outline: dict, provider_id: str = None, model_name: str = None, enabled: bool = True) -> list:
    """返回并发波列表 list[list[int]]。enabled=False 或失败 → 全串行。"""
    chapters = outline.get("chapters", []) or []
    n = len(chapters)
    if n == 0:
        return []
    if not enabled or n == 1:
        return _sequential_waves(n)

    try:
        from services.llm_service import get_llm_service

        service = get_llm_service(provider_id, model_name)
        ch_list = "\n".join(
            f'{i}. {c.get("title","")}：{c.get("summary","")}' for i, c in enumerate(chapters)
        )
        system_prompt = (
            "你是书籍生成的并发调度分析器。给定章节列表，判断每一章在写作时是否**强依赖前面某些章节的具体内容**"
            "（例如：本章是对前面某章的直接延续/总结/回指）。只有强依赖才登记，泛泛的主题相关不算依赖。"
            "依赖只能指向更靠前的章节编号。\n"
            '只输出 JSON：{"dependencies": {"章节号": [被依赖的更前章节号, ...], ...}}，无依赖的章节可省略或给空数组。'
        )
        user_message = f"章节列表：\n{ch_list}\n\n请输出依赖 JSON。"
        raw = service.generate_sync(system_prompt, user_message, max_tokens=800)
        data = _extract_json(raw) or {}
        dep_raw = data.get("dependencies", {}) or {}
        deps = {}
        for k, v in dep_raw.items():
            try:
                ki = int(k)
            except (TypeError, ValueError):
                continue
            deps[ki] = [int(x) for x in v if isinstance(x, (int, str)) and str(x).lstrip("-").isdigit()]
        return _topo_waves(n, deps)
    except Exception as e:
        print(f"[router] plan_waves failed, fallback sequential: {e}")
        return _sequential_waves(n)
