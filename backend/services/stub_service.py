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


def _edit_content(content: str, chapter_index: int, taken_ids: set, resolvable: dict):
    """纯函数：编辑本章 content，登记/兑现 stub 不直接落库，而是返回操作清单。

    - taken_ids: 已占用的 id 集合（用于新 stub 去重；调用方负责包含「已登记 + 本波已缓冲」的 id）
    - resolvable: {id: stub} 可被兑现的（前文已登记且尚未兑现）stub；同一波内重复兑现同一 id 会被丢弃
    返回 (new_content, new_stubs, resolved_ops)；resolved_ops 为 [(sid, dst_chapter)]。
    """
    new_stubs = []
    resolved_ops = []
    local_taken = set(taken_ids)
    claimed = set()  # 本次调用已认领兑现的 id（防同一段落内重复 resolve）

    def repl(m):
        raw = m.group(1).strip()
        try:
            spec = json.loads(raw)
        except json.JSONDecodeError:
            return m.group(0)
        tool = (spec.get("tool") or "").lower()

        if tool == "stub":
            sid = _slug(spec.get("id") or f"c{chapter_index}_{len(new_stubs)}")
            base, k = sid, 1
            while sid in local_taken:
                sid = f"{base}_{k}"; k += 1
            local_taken.add(sid)
            new_stubs.append({
                "id": sid,
                "where": spec.get("where", ""),
                "what": spec.get("what", ""),
                "source_chapter": chapter_index,
                "src_anchor": f"s_{sid}",
                "resolved": False,
            })
            return f"`⚓s_{sid}`"

        if tool == "resolve":
            sid = _slug(spec.get("id") or "")
            if sid not in resolvable or sid in claimed:
                return ""  # 不存在 / 已被（含本波其它章节）认领 → 丢弃
            claimed.add(sid)
            resolved_ops.append((sid, chapter_index))
            return f"`⚓d_{sid}`\n\n[↩ 返回前文](#s_{sid})"

        return m.group(0)  # 其它工具原样保留，交给 content_tools

    return TOOL_BLOCK_RE.sub(repl, content), new_stubs, resolved_ops


def _commit_ops(open_stubs: list, new_stubs: list, resolved_ops: list):
    """把 _edit_content 产出的操作落到 open_stubs（调用方需保证单线程/持锁）。"""
    open_stubs.extend(new_stubs)
    by_id = {s["id"]: s for s in open_stubs}
    for sid, dchap in resolved_ops:
        stub = by_id.get(sid)
        if stub and not stub.get("resolved"):
            stub["resolved"] = True
            stub["dst_chapter"] = dchap
            stub["dst_anchor"] = f"d_{sid}"


def process_chapter(content: str, chapter_index: int, open_stubs: list) -> str:
    """处理一章：登记新 stub、兑现已有 stub，放置锚点。立即落库（串行/非冻结路径）。"""
    if not content or "```tool" not in content:
        return content
    taken = {s["id"] for s in open_stubs}
    resolvable = {s["id"]: s for s in open_stubs if not s.get("resolved")}
    new_content, new_stubs, resolved_ops = _edit_content(content, chapter_index, taken, resolvable)
    _commit_ops(open_stubs, new_stubs, resolved_ops)
    return new_content


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
    """线程安全的 stub 仓库 + 并发一致性控制。

    并发步（parallel wave）执行期间，章节的「读快照→长时间 LLM 生成→写回」是个长窗口，
    若期间另一章登记了 stub，本章用的是步前快照——这就是 stale read。为消除这种时序不确定，
    引入「冻结 + 延迟提交 + barrier」：
      · freeze()：进并发步前冻结。期间 prompt() 一律返回**步前的同一份快照**（所有并发章节看到
        的待办完全一致，与谁先调无关）；process() 不直接落库，登记/兑现操作排队到缓冲区。
      · unfreeze()：步结束、回到单线程的 barrier，把缓冲区操作统一提交，对下一步可见。
    串行步不冻结：单线程，process() 立即落库，下一章天然读到最新。
    """

    def __init__(self):
        self._stubs = []
        self._lock = threading.RLock()
        self._frozen = False
        self._frozen_snapshot = []   # 冻结时拍下的步前待办（prompt 期间恒定）
        self._wave_new = []          # 本波缓冲：新登记的 stub
        self._wave_resolved = {}     # 本波缓冲：{sid: dst_chapter} 已认领的兑现

    def prompt(self) -> str:
        with self._lock:
            base = self._frozen_snapshot if self._frozen else self._stubs
            return stubs_prompt(list(base))

    def process(self, content: str, chapter_index: int) -> str:
        if not content or "```tool" not in content:
            return content
        with self._lock:
            if not self._frozen:
                # 串行/非并发：立即落库
                return process_chapter(content, chapter_index, self._stubs)
            # 冻结中：基于「步前快照」做兑现查找、用「已登记+本波缓冲」做去重，操作进缓冲区
            taken = {s["id"] for s in self._stubs} | {s["id"] for s in self._wave_new}
            resolvable = {
                s["id"]: s for s in self._frozen_snapshot
                if not s.get("resolved") and s["id"] not in self._wave_resolved
            }
            new_content, new_stubs, resolved_ops = _edit_content(content, chapter_index, taken, resolvable)
            self._wave_new.extend(new_stubs)
            for sid, dchap in resolved_ops:
                self._wave_resolved.setdefault(sid, dchap)  # 先到先得，防同一波重复兑现
            return new_content

    def freeze(self):
        """进并发步前调用：冻结，prompt 锁定步前快照，写操作转入缓冲。"""
        with self._lock:
            self._frozen = True
            self._frozen_snapshot = list(self._stubs)
            self._wave_new = []
            self._wave_resolved = {}

    def unfreeze(self) -> bool:
        """并发步结束的 barrier：单线程统一提交缓冲操作。返回是否有变更。"""
        with self._lock:
            changed = bool(self._wave_new or self._wave_resolved)
            resolved_ops = list(self._wave_resolved.items())
            _commit_ops(self._stubs, self._wave_new, resolved_ops)
            self._frozen = False
            self._frozen_snapshot = []
            self._wave_new = []
            self._wave_resolved = {}
            return changed

    def stitch(self, chapters: list) -> None:
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
