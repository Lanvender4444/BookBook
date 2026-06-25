"""ReAct 智能体可用的工具：web 搜索 + 本地知识库检索。

设计：
- 工具用纯函数实现，输入 query（知识库另需 source_ids），返回精炼的「观察」文本。
- web_search 支持可配置 provider（Tavily / Serper / Brave），key 存 AppSetting 表或环境变量；
  未配置时返回明确提示，ReAct 循环可据此改走知识库或直接写作，不会崩。
"""

import os
import json
import re

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


# ---------------------------------------------------------------- 论文搜寻（学术）

def search_papers(query: str, max_results: int = 5) -> str:
    """学术论文搜寻：arXiv（主）+ Crossref（补）。两者均无需 API key，开箱即用。"""
    results = []
    try:
        results = _search_arxiv(query, max_results)
    except Exception as e:
        print(f"[papers] arxiv failed: {e}")
    if len(results) < max_results:
        try:
            results += _search_crossref(query, max_results - len(results))
        except Exception as e:
            print(f"[papers] crossref failed: {e}")
    if not results:
        return f"[search_papers]：未找到与「{query}」相关的论文。"

    lines = [f"论文搜寻「{query}」结果："]
    for i, r in enumerate(results[:max_results], 1):
        authors = ", ".join(r.get("authors", [])[:4])
        if len(r.get("authors", [])) > 4:
            authors += " 等"
        summary = (r.get("summary", "") or "").strip().replace("\n", " ")
        if len(summary) > 320:
            summary = summary[:320] + "…"
        meta = " · ".join(x for x in [r.get("source"), r.get("year"), authors] if x)
        lines.append(f"{i}. {r.get('title','').strip()}\n   {meta}\n   {summary}\n   {r.get('url','')}")
    return "\n".join(lines)


def _search_arxiv(query: str, n: int):
    import xml.etree.ElementTree as ET

    with httpx.Client(timeout=SEARCH_TIMEOUT) as c:
        resp = c.get(
            "http://export.arxiv.org/api/query",
            params={"search_query": f"all:{query}", "start": 0, "max_results": n},
        )
        resp.raise_for_status()
        text = resp.text
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(text)
    out = []
    for e in root.findall("a:entry", ns):
        title = (e.findtext("a:title", default="", namespaces=ns) or "").strip()
        summary = (e.findtext("a:summary", default="", namespaces=ns) or "").strip()
        published = (e.findtext("a:published", default="", namespaces=ns) or "")[:4]
        authors = [a.findtext("a:name", default="", namespaces=ns) for a in e.findall("a:author", ns)]
        link = ""
        for li in e.findall("a:link", ns):
            if li.get("type") == "text/html" or li.get("rel") == "alternate":
                link = li.get("href", "")
                break
        out.append({"title": title, "summary": summary, "authors": authors, "year": published, "url": link, "source": "arXiv"})
    return out


def _search_crossref(query: str, n: int):
    with httpx.Client(timeout=SEARCH_TIMEOUT) as c:
        resp = c.get(
            "https://api.crossref.org/works",
            params={"query": query, "rows": n, "select": "title,author,abstract,URL,issued,container-title"},
            headers={"User-Agent": "BookBook/1.0 (mailto:app@bookbook.local)"},
        )
        resp.raise_for_status()
        items = resp.json().get("message", {}).get("items", [])
    out = []
    for it in items:
        title = (it.get("title") or [""])[0]
        authors = [f"{a.get('given','')} {a.get('family','')}".strip() for a in it.get("author", [])]
        year = ""
        try:
            year = str(it.get("issued", {}).get("date-parts", [[None]])[0][0] or "")
        except Exception:
            year = ""
        abstract = re.sub(r"<[^>]+>", "", it.get("abstract", "") or "")
        out.append({"title": title, "summary": abstract, "authors": authors, "year": year, "url": it.get("URL", ""), "source": "Crossref"})
    return out


# ---------------------------------------------------------------- 工具描述（给模型看）

def tools_spec(knowledge_available: bool, web_available: bool, papers_available: bool = True) -> str:
    specs = []
    if web_available:
        specs.append('- "web_search": 联网搜索最新/外部事实信息。参数 {"query": "搜索词"}')
    if papers_available:
        specs.append('- "search_papers": 学术论文搜寻（arXiv/Crossref），用于需要严谨学术依据时。参数 {"query": "检索词"}')
    if knowledge_available:
        specs.append('- "search_knowledge": 检索用户提供的本地知识库（资料库/风格/续写原文）。参数 {"query": "检索词"}')
    return "\n".join(specs)


def run_tool(name: str, query: str, source_ids: list[str]) -> str:
    if name == "web_search":
        return web_search(query)
    if name == "search_papers":
        return search_papers(query)
    if name == "search_knowledge":
        return search_knowledge(query, source_ids)
    return f"[未知工具]：{name}"
