"""跨章节 Stub（前向引用 / 占位）系统。

场景：写第 N 章时，AI 发现「某些内容应留到后面的章节再展开」，于是登记一个 stub，
包含「加到哪里(where)」和「要加什么(what)」。等后面某一章真正写到这块内容时，AI 用
resolve 回调这个 stub —— 我们在【登记位置(源)】插入一个跳转到【兑现位置(目标)】的链接，
并把该 stub 从待办列表删除。

调用协议（模型在正文中用 ```tool 块）：
  登记： ```tool
         {"tool":"stub","id":"唯一短id","where":"后文要展开的位置/主题","what":"要补充的内容简述"}
         ```
  兑现： ```tool
         {"tool":"resolve","id":"对应的stub id"}
         ```

实现要点：
- process_chapter：在生成完一章后调用，登记/兑现 stub，并在源/目标处放置锚点 token。
- stitch：所有章节生成完后调用，把已兑现 stub 的「源锚点」替换为指向目标的跳转链接，
  清理未兑现 stub 的残留锚点。
- 锚点用行内代码 token ``⚓ID`` 表示，前端 Reader 渲染为隐藏的 <span id=ID>；
  跳转链接用普通 Markdown 链接 [文字](#ID)，Reader 拦截做平滑滚动。
"""

import json
import re
import threading

TOOL_BLOCK_RE = re.compile(r"```tool\s*\n(.*?)```", re.S)


def _slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "", str(s))[:40] or "x"


def stubs_prompt(open_stubs: list) -> str:
    """生成注入章节 prompt 的 stub 说明 + 当前待办列表。"""
    head = (
        "【跨章占位 Stub】\n"
        "- 如果本章引入了某个概念，但它的详细展开更适合放到后面的章节，请用工具登记一个 stub：\n"
        '  ```tool\n{"tool":"stub","id":"唯一英文短id","where":"后文将展开的位置/主题","what":"要补充的内容简述"}\n```\n'
        "  系统会在此处留锚点，等后面兑现时自动生成跳转链接。\n"
        "- 如果本章正是某个已登记 stub 的兑现位置，请正常写出该内容，并在写完处用工具兑现：\n"
        '  ```tool\n{"tool":"resolve","id":"对应的stub id"}\n```\n'
        "  不要硬凑：只在内容确实对应时兑现。"
    )
    if open_stubs:
        items = "\n".join(
            f'  - id="{s["id"]}"：where=「{s.get("where","")}」 what=「{s.get("what","")}」'
            for s in open_stubs if not s.get("resolved")
        )
        if items:
            head += "\n\n当前待兑现的 stub：\n" + items
    return head


def process_chapter(content: str, chapter_index: int, open_stubs: list) -> str:
    """处理一章：登记新 stub、兑现已有 stub，放置锚点。原地更新 open_stubs。"""
    if not content or "```tool" not in content:
        return content

    by_id = {s["id"]: s for s in open_stubs}

    def repl(m):
        raw = m.group(1).strip()
        try:
            spec = json.loads(raw)
        except json.JSONDecodeError:
            return m.group(0)  # 非法 JSON 保留原块，交给后续 content_tools 处理
        tool = (spec.get("tool") or "").lower()

        if tool == "stub":
            sid = _slug(spec.get("id") or f"c{chapter_index}_{len(open_stubs)}")
            # 避免重复 id
            base, k = sid, 1
            while sid in by_id:
                sid = f"{base}_{k}"; k += 1
            stub = {
                "id": sid,
                "where": spec.get("where", ""),
                "what": spec.get("what", ""),
                "source_chapter": chapter_index,
                "src_anchor": f"s_{sid}",
                "resolved": False,
            }
            open_stubs.append(stub)
            by_id[sid] = stub
            # 源处放锚点（待 stitch 时追加跳转链接）
            return f"`⚓s_{sid}`"

        if tool == "resolve":
            sid = _slug(spec.get("id") or "")
            stub = by_id.get(sid)
            if not stub or stub.get("resolved"):
                return ""  # 找不到对应 stub 或已兑现，丢弃该块
            stub["resolved"] = True
            stub["dst_chapter"] = chapter_index
            stub["dst_anchor"] = f"d_{sid}"
            # 目标处放锚点 + 返回源的反向链接
            return f"`⚓d_{sid}`\n\n[↩ 返回前文](#s_{sid})"

        # 其它工具（table/svg/未知）原样保留，交给 content_tools
        return m.group(0)

    return TOOL_BLOCK_RE.sub(repl, content)


def stitch(chapters: list, open_stubs: list) -> None:
    """全书生成完后的缝合：已兑现 stub 的源锚点追加跳转链接；未兑现的清理锚点。"""
    for stub in open_stubs:
        sc = stub.get("source_chapter")
        if sc is None or sc >= len(chapters):
            continue
        src_token = f"`⚓s_{stub['id']}`"
        if stub.get("resolved"):
            # 源：保留锚点（供反向链接定位）+ 追加跳转到目标
            replacement = f"`⚓s_{stub['id']}`（[详见后文 ➜](#d_{stub['id']})）"
            chapters[sc] = chapters[sc].replace(src_token, replacement)
        else:
            # 未兑现：移除源锚点，避免残留
            chapters[sc] = chapters[sc].replace(src_token, "")


class StubStore:
    """线程安全的 stub 仓库。章节并发执行时，对 open_stubs 的读/写都过锁。"""

    def __init__(self):
        self._stubs = []
        self._lock = threading.RLock()

    def prompt(self) -> str:
        """快照当前待办，生成注入章节 prompt 的说明。"""
        with self._lock:
            return stubs_prompt(list(self._stubs))

    def process(self, content: str, chapter_index: int) -> str:
        """登记/兑现本章 stub（加锁）。"""
        with self._lock:
            return process_chapter(content, chapter_index, self._stubs)

    def stitch(self, chapters: list) -> None:
        """全书缝合（此时通常已单线程，仍加锁以防万一）。"""
        with self._lock:
            stitch(chapters, self._stubs)

    def snapshot(self) -> list:
        with self._lock:
            return list(self._stubs)


def strip_anchor_tokens(text: str) -> str:
    """导出/降级时移除锚点 token，并把内部跳转链接降级为纯文字。"""
    if not text:
        return text
    text = re.sub(r"`⚓[^`]*`", "", text)
    text = re.sub(r"（?\[([^\]]+)\]\(#[^)]+\)）?", r"\1", text)
    return text
