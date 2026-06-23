"""ReAct 智能体可用的工具：web 搜索 + 本地知识库检索。

设计：
- 工具用纯函数实现，输入 query（知识库另需 source_ids），返回精炼的「观察」文本。
- web_search 支持可配置 provider（Tavily / Serper / Brave），key 存 AppSetting 表或环境变量；
  未配置时返回明确提示，ReAct 循环可据此改走知识库或直接写作，不会崩。
"""

import os
import json

import httpx
from database import SessionLocal
from models import AppSetting

SEARCH_TIMEOUT = httpx.Timeout(20.0, connect=8.0)


# ---------------------------------------------------------------- 设置读取

def get_setting(key: str, default: str = "") -> str:
    db = SessionLocal()
    try:
        row = db.query(AppSetting).filter(AppSetting.key == key).first()
        if row and row.value:
            return row.value
    finally:
        db.close()
    return os.getenv(key.upper(), default)


def set_setting(key: str, value: str):
    db = SessionLocal()
    try:
        row = db.query(AppSetting).filter(AppSetting.key == key).first()
        if row:
            row.value = value
        else:
            db.add(AppSetting(key=key, value=value))
        db.commit()
    finally:
        db.close()


def web_search_configured() -> bool:
    provider = get_setting("search_provider", "")
    key = get_setting("search_api_key", "")
    return bool(provider and key)


# ---------------------------------------------------------------- web 搜索

def web_search(query: str, max_results: int = 5) -> str:
    """联网搜索，返回带标题/摘要/链接的精炼结果文本。未配置则返回提示。"""
    provider = (get_setting("search_provider", "") or "").lower()
    api_key = get_setting("search_api_key", "")
    if not provider or not api_key:
        return "[web_search 未配置]：未设置搜索 provider 或 API key，无法联网搜索。请改用知识库或依据已有知识写作。"

    try:
        if provider == "tavily":
            results = _search_tavily(query, api_key, max_results)
        elif provider == "serper":
            results = _search_serper(query, api_key, max_results)
        elif provider == "brave":
            results = _search_brave(query, api_key, max_results)
        else:
            return f"[web_search 错误]：未知 provider '{provider}'（支持 tavily/serper/brave）。"
    except Exception as e:
        return f"[web_search 失败]：{e}"

    if not results:
        return f"[web_search]：未找到与「{query}」相关的结果。"

    lines = [f"web 搜索「{query}」结果："]
    for i, r in enumerate(results[:max_results], 1):
        title = r.get("title", "").strip()
        snippet = r.get("snippet", "").strip().replace("\n", " ")
        url = r.get("url", "")
        lines.append(f"{i}. {title}\n   {snippet}\n   来源: {url}")
    return "\n".join(lines)


def _search_tavily(query, api_key, max_results):
    with httpx.Client(timeout=SEARCH_TIMEOUT) as c:
        resp = c.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": max_results, "search_depth": "basic"},
        )
        resp.raise_for_status()
        data = resp.json()
    return [
        {"title": r.get("title", ""), "snippet": r.get("content", ""), "url": r.get("url", "")}
        for r in data.get("results", [])
    ]


def _search_serper(query, api_key, max_results):
    with httpx.Client(timeout=SEARCH_TIMEOUT) as c:
        resp = c.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": max_results},
        )
        resp.raise_for_status()
        data = resp.json()
    return [
        {"title": r.get("title", ""), "snippet": r.get("snippet", ""), "url": r.get("link", "")}
        for r in data.get("organic", [])
    ]


def _search_brave(query, api_key, max_results):
    with httpx.Client(timeout=SEARCH_TIMEOUT) as c:
        resp = c.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
            params={"q": query, "count": max_results},
        )
        resp.raise_for_status()
        data = resp.json()
    return [
        {"title": r.get("title", ""), "snippet": r.get("description", ""), "url": r.get("url", "")}
        for r in data.get("web", {}).get("results", [])
    ]


# ---------------------------------------------------------------- 知识库检索

def search_knowledge(query: str, source_ids: list[str], top_k: int = 5) -> str:
    """检索本地知识库（写作卡关联的知识源），返回相关片段。"""
    from services.rag_service import retrieve

    if not source_ids:
        return "[search_knowledge]：当前没有可检索的本地知识库（写作卡未关联任何知识源）。"
    try:
        hits = retrieve(query, source_ids, top_k)
    except Exception as e:
        return f"[search_knowledge 失败]：{e}"
    if not hits:
        return f"[search_knowledge]：知识库中未找到与「{query}」相关的内容。"

    lines = [f"本地知识库「{query}」检索结果："]
    for i, h in enumerate(hits, 1):
        text = (h.get("text") or "").strip().replace("\n", " ")
        if len(text) > 500:
            text = text[:500] + "…"
        lines.append(f"{i}. 〔{h.get('source_name', '')}/{h.get('category', '')}〕{text}")
    return "\n".join(lines)


# ---------------------------------------------------------------- 工具描述（给模型看）

def tools_spec(knowledge_available: bool, web_available: bool) -> str:
    specs = []
    if web_available:
        specs.append('- "web_search": 联网搜索最新/外部事实信息。参数 {"query": "搜索词"}')
    if knowledge_available:
        specs.append('- "search_knowledge": 检索用户提供的本地知识库（资料库/风格/续写原文）。参数 {"query": "检索词"}')
    return "\n".join(specs)


def run_tool(name: str, query: str, source_ids: list[str]) -> str:
    if name == "web_search":
        return web_search(query)
    if name == "search_knowledge":
        return search_knowledge(query, source_ids)
    return f"[未知工具]：{name}"
