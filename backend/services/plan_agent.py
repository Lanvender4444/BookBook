"""Plan 智能体（Meaning Table 的唯一拥有者与唯一写者）。

设计：
- Plan 在写大纲时额外生成一份 **Meaning Table（意图表 JSON）**：详细规划全书意图、
  每一章的意图，以及它「承接前文什么 / 为后文铺垫什么」（前后部分）。
- **写权限不变量**：这份 JSON 只有 Plan（本对象内部、串行化的 consult/build）能修改。
  Route 和 Execute 都不能改它，只能通过 `consult()` 向 Plan 提问。
- **Route → Plan 咨询**：Route 带着疑问 + JSON 定位（哪一章/全书）+ 上下文向 Plan 提问。
  Plan 做两件事：(1) 想清楚回复 Route 什么；(2) 决定是否修改意图表（allow_modify=True 时才可能改）。
- **Execute → Plan 咨询**：每个并发章节线程可自行决定「是否向 Plan 提问详细意图」。
  这类咨询 **只读**（allow_modify=False），绝不修改意图表。

并发：意图表的所有读改都在锁内；consult 整体串行（一次只服务一个咨询），
保证「只有 Plan 改表」且改表过程一致。
"""

import json
import re
import threading


def _extract_json(text: str):
    if not text:
        return None
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    raw = m.group(0)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # 容错：截到第一个平衡花括号
        depth = 0
        for i, ch in enumerate(raw):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(raw[: i + 1])
                    except json.JSONDecodeError:
                        return None
        return None


def _deep_merge(base: dict, patch: dict):
    """把 patch 深合并进 base（就地）。list/标量直接覆盖，dict 递归。"""
    for k, v in (patch or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


class PlanAgent:
    """长生命周期的 Plan 角色：拥有并独占修改 Meaning Table。"""

    def __init__(self, provider_id=None, model_name=None, language="zh-CN"):
        self.provider_id = provider_id
        self.model_name = model_name
        self.language = language
        self._table = None
        self._table_lock = threading.RLock()   # 保护表的读改
        self._consult_lock = threading.Lock()  # 串行化 Plan 的思考/改表
        self._ready = False
        # ---- 一致性控制：版本号 + 并发期冻结 + 延迟改表 ----
        # 解决"A 改表、B 正在并发跑导致 B 读到旧意图"的陈旧读问题：
        # 并发步执行期间冻结表（freeze），期间产生的修改不立即生效而是排队，
        # 等并发步全部结束、回到单线程 barrier 时再统一应用（unfreeze），并递增版本号。
        self._version = 0
        self._frozen = False
        self._pending = []  # 冻结期间排队的待应用 patch

    # ---- 构建意图表（Plan 写） ----
    def build(self, outline: dict, prompt: str, requirements: dict) -> dict | None:
        from services.llm_service import get_llm_service, _get_language_name

        lang_name = _get_language_name(requirements.get("language", self.language))
        chapters = outline.get("chapters", []) or []
        ch_list = "\n".join(f'{i}. {c.get("title","")}：{c.get("summary","")}' for i, c in enumerate(chapters))
        system_prompt = (
            f"你是全书的总规划者（Plan）。基于大纲，为整本书生成一份「意图表(Meaning Table)」，"
            f"用 {lang_name} 填写文字字段。它要详细刻画全书意图与每一章的意图、以及每章的前后衔接。\n"
            "只输出 JSON，结构：\n"
            "{\n"
            '  "book_intent": "全书要达成的核心意图/主旨",\n'
            '  "arc": "整体叙事/论证脉络（开端→发展→高潮→收束）",\n'
            '  "chapters": [\n'
            '    {"index":0, "title":"...", "intent":"本章意图（要让读者获得什么）",\n'
            '     "before":"承接前文的什么（第0章可写引入背景）",\n'
            '     "after":"为后文铺垫/埋设什么",\n'
            '     "key_points":["要点1","要点2"]}\n'
            "  ]\n"
            "}\n"
            "chapters 数组长度必须与大纲章节数一致，index 从 0 顺序递增。"
        )
        user_message = f"书名：{outline.get('title','')}\n简介：{outline.get('description','')}\n用户需求：{prompt}\n\n章节：\n{ch_list}\n\n请输出意图表 JSON。"
        try:
            service = get_llm_service(self.provider_id, self.model_name)
            raw = service.generate_sync(system_prompt, user_message, max_tokens=2000)
            table = _extract_json(raw)
            if not table or "chapters" not in table:
                return None
            with self._table_lock:
                self._table = table
                self._ready = True
            return table
        except Exception as e:
            print(f"[Plan] build meaning table failed: {e}")
            return None

    @property
    def ready(self) -> bool:
        return self._ready

    # ---- 版本与并发冻结（一致性控制） ----
    def version(self) -> int:
        with self._table_lock:
            return self._version

    def freeze(self):
        """进入并发步前调用：冻结表，期间的改表请求改为排队。"""
        with self._table_lock:
            self._frozen = True

    def unfreeze(self) -> bool:
        """并发步结束、回到单线程 barrier 时调用：统一应用排队的改表并递增版本。

        返回是否发生了实际修改。此时没有其它线程在跑，更新对下一步可见，无陈旧读。
        """
        with self._table_lock:
            self._frozen = False
            applied = False
            for patch in self._pending:
                if self._apply_patch_locked(patch):
                    applied = True
            self._pending = []
            return applied

    # ---- 只读快照（Route 携带；Execute 不直接持有） ----
    def snapshot(self) -> dict | None:
        with self._table_lock:
            return json.loads(json.dumps(self._table)) if self._table else None

    def restore(self, table: dict | None, version: int = 0) -> bool:
        """断点续传：从持久化快照恢复意图表，跳过昂贵的 build（不再调 LLM）。"""
        if not table or "chapters" not in table:
            return False
        with self._table_lock:
            self._table = json.loads(json.dumps(table))
            self._version = int(version or 0)
            self._frozen = False
            self._pending = []
            self._ready = True
        return True

    def _chapter_slice(self, index) -> dict | None:
        with self._table_lock:
            if not self._table:
                return None
            for ch in self._table.get("chapters", []):
                if ch.get("index") == index:
                    return json.loads(json.dumps(ch))
            return None

    def _locate(self, locator: dict) -> str:
        """根据定位取出意图表的相关切片，喂给 Plan 思考。"""
        if not locator:
            return json.dumps(self.snapshot() or {}, ensure_ascii=False)[:2000]
        scope = locator.get("scope", "book")
        if scope == "chapter" and "index" in locator:
            sl = self._chapter_slice(locator["index"])
            with self._table_lock:
                book = {"book_intent": (self._table or {}).get("book_intent", ""), "arc": (self._table or {}).get("arc", "")}
            return json.dumps({"book": book, "chapter": sl}, ensure_ascii=False)
        return json.dumps(self.snapshot() or {}, ensure_ascii=False)[:2000]

    # ---- 咨询入口（Route allow_modify=True；Execute allow_modify=False） ----
    def consult(self, asker: str, question: str, locator: dict = None, context: str = "",
                allow_modify: bool = False, on_event=None) -> dict:
        """返回 {"reply": str, "modified": bool}。allow_modify=False 时绝不改表。"""
        if not self._ready:
            return {"reply": "", "modified": False}

        from services.llm_service import get_llm_service

        with self._consult_lock:  # 串行化：一次只服务一个咨询
            sliced = self._locate(locator or {})
            modify_clause = (
                '是否需要据此**修订意图表**（modify=true 并给出 patch）。'
                if allow_modify
                else "（注意：本次咨询为只读，你不能修改意图表，patch 一律忽略。）"
            )
            system_prompt = (
                f"你是全书总规划者（Plan），意图表的唯一拥有者。下游环节「{asker}」带着疑问来咨询。\n"
                "请：(1) 想清楚要回复对方什么（reply，简明、可操作）；(2) 判断" + modify_clause + "\n"
                "只输出 JSON：{\"reply\":\"给对方的答复\", \"modify\": true/false, "
                "\"patch\": {可选，对意图表的局部修订，如 {\\\"chapters\\\":{\\\"2\\\":{\\\"intent\\\":\\\"...\\\"}}} 或 {\\\"book_intent\\\":\\\"...\\\"}}}"
            )
            user_message = f"相关意图表切片：\n{sliced}\n\n对方的疑问：{question}\n补充上下文：{context}\n\n请输出 JSON。"
            try:
                service = get_llm_service(self.provider_id, self.model_name)
                raw = service.generate_sync(system_prompt, user_message, max_tokens=900)
            except Exception as e:
                return {"reply": "", "modified": False}

            data = _extract_json(raw) or {}
            reply = (data.get("reply") or "").strip()
            modified = False
            deferred = False

            if allow_modify and data.get("modify") and isinstance(data.get("patch"), dict):
                with self._table_lock:
                    if self._frozen:
                        # 并发步进行中：不立即改表（否则正在跑的其它章节会读到旧/新不一致），
                        # 排队到下一个 barrier（unfreeze）再统一生效。
                        self._pending.append(data["patch"])
                        deferred = True
                    else:
                        modified = self._apply_patch_locked(data["patch"])

            if on_event:
                try:
                    on_event({"asker": asker, "question": question, "reply": reply,
                              "modified": modified, "deferred": deferred, "version": self.version()})
                except Exception:
                    pass
            return {"reply": reply, "modified": modified, "deferred": deferred, "version": self.version()}

    # ---- 唯一改表入口（调用方必须已持 _table_lock；递增版本号） ----
    def _apply_patch_locked(self, patch: dict) -> bool:
        if not self._table:
            return False
        patch = dict(patch)
        # chapters 以 index 字典形式 patch：{"chapters": {"2": {...}}}
        ch_patch = patch.get("chapters")
        if isinstance(ch_patch, dict):
            for k, v in ch_patch.items():
                try:
                    idx = int(k)
                except (TypeError, ValueError):
                    continue
                for ch in self._table.get("chapters", []):
                    if ch.get("index") == idx and isinstance(v, dict):
                        _deep_merge(ch, v)
            patch = {kk: vv for kk, vv in patch.items() if kk != "chapters"}
        # 其余 book 级字段
        _deep_merge(self._table, patch)
        self._version += 1   # 任何成功修改都递增版本，供陈旧读检测
        return True

    # ---- 供 Execute 写章前注入：本章意图说明（来自咨询或直接切片） ----
    def chapter_intent_note(self, index) -> str:
        sl = self._chapter_slice(index)
        if not sl:
            return ""
        parts = [f"【本章意图（来自总规划）】意图：{sl.get('intent','')}"]
        if sl.get("before"):
            parts.append(f"承接前文：{sl['before']}")
        if sl.get("after"):
            parts.append(f"为后文铺垫：{sl['after']}")
        if sl.get("key_points"):
            parts.append("要点：" + "；".join(sl["key_points"]))
        return "\n".join(parts)
