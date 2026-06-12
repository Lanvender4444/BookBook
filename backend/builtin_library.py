"""内置知识库：风格库 / 写作指导 的预置条目。

内容以 Python 常量存储（而非数据文件），这样 PyInstaller --onefile 打包零配置。
要新增内置条目，往 BUILTIN_SOURCES / BUILTIN_CARDS 里加 dict 即可，
id 必须以 "builtin-" 开头且全局唯一；应用启动时自动种子化（已存在则更新内容）。

每个 source: {id, name, category, content, prompt, language(可选)}
category: writing_guide | style | reference | continuation
"""

BUILTIN_SOURCES = [
    # ---------------- 风格库示例 ----------------
    {
        "id": "builtin-style-shenrujianchu",
        "name": "深入浅出",
        "category": "style",
        "prompt": "模仿此风格的讲解方式：先具象后抽象，多用生活化类比，每个概念配一个例子。",
        "content": (
            "「深入浅出」风格样本：\n\n"
            "想象你第一次走进一家咖啡店。你不需要知道咖啡机的内部构造，"
            "只要告诉店员要拿铁还是美式——这就是“接口”与“实现”的区别。"
            "程序设计里的封装，本质上就是咖啡店的点单台：把复杂留给后厨，把简单留给顾客。\n\n"
            "这种风格的要点：\n"
            "1. 任何抽象概念出场前，先给一个读者亲身经历过的场景。\n"
            "2. 类比之后立刻点破映射关系，不让读者自己猜。\n"
            "3. 句子短，段落短，一段只讲一件事。\n"
            "4. 在章节结尾用一两句话把本章所有类比收束回正式术语。"
        ),
    },
    {
        "id": "builtin-style-jazz-age",
        "name": "美国爵士乐时代风格",
        "category": "style",
        "prompt": "模仿菲茨杰拉德式的爵士乐时代文风：华丽而忧郁，物质的喧嚣与精神的失落并置。",
        "content": (
            "「爵士乐时代」风格样本：\n\n"
            "派对的灯光在长岛的夜色里燃到天明，香槟塔的金色泡沫顺着水晶杯沿滑落，"
            "像那个年代所有来不及兑现的承诺。人们在萨克斯风的呜咽里跳查尔斯顿舞，"
            "笑声越响亮，眼底的疲惫就越深。绿色的灯光在码头尽头明明灭灭，"
            "所有人都伸出手去，以为抓住的是未来，其实只是昨夜的余烬。\n\n"
            "这种风格的要点：\n"
            "1. 长句铺陈感官细节：灯光、酒、音乐、衣料的质感。\n"
            "2. 繁华与幻灭并置，每段华丽描写后埋一笔失落。\n"
            "3. 善用象征物（灯光、汽车、钟表）承载主题。\n"
            "4. 叙述者保持一种既身在其中又冷眼旁观的距离感。"
        ),
    },
    # ---------------- 写作指导示例 ----------------
    {
        "id": "builtin-guide-structure",
        "name": "章节结构指导（总-分-总）",
        "category": "writing_guide",
        "prompt": "严格按照本指导组织每一章的结构。",
        "content": (
            "章节结构写作指导：\n\n"
            "1. 开篇（约10%）：用一个问题、场景或冲突引入本章主题，说明读者读完能获得什么。\n"
            "2. 主体（约80%）：按逻辑顺序展开 2-4 个小节；每个小节遵循「论点 → 论据/例子 → 小结」；"
            "小节之间用过渡句衔接，禁止生硬跳转。\n"
            "3. 收尾（约10%）：回应开篇的问题，总结本章要点，并用一句话预告下一章。\n"
            "4. 全书章节篇幅保持均衡，避免头重脚轻。"
        ),
    },
]

# 内置写作卡（组合内置知识源）
BUILTIN_CARDS = [
    {
        "id": "builtin-card-popsci",
        "name": "科普写作（深入浅出）",
        "writing_guide_ids": ["builtin-guide-structure"],
        "style_ids": ["builtin-style-shenrujianchu"],
        "reference_ids": [],
        "continuation_ids": [],
        "extra_requirements": "面向零基础读者，避免堆砌术语；必要的术语第一次出现时给出通俗解释。",
    },
]


def seed_builtins():
    """启动时种子化内置库：不存在则插入，存在则刷新内容；之后异步建索引。"""
    from database import SessionLocal
    from models import KnowledgeSource, WritingCard

    db = SessionLocal()
    need_index = []
    try:
        for item in BUILTIN_SOURCES:
            row = db.query(KnowledgeSource).filter(KnowledgeSource.id == item["id"]).first()
            if row is None:
                row = KnowledgeSource(
                    id=item["id"],
                    name=item["name"],
                    category=item["category"],
                    link_mode="builtin",
                    text_content=item["content"],
                    prompt=item.get("prompt"),
                    language=item.get("language"),
                    builtin=True,
                    index_status="pending",
                )
                db.add(row)
                need_index.append(item["id"])
            elif row.text_content != item["content"] or row.prompt != item.get("prompt"):
                row.text_content = item["content"]
                row.prompt = item.get("prompt")
                row.name = item["name"]
                row.index_status = "pending"
                need_index.append(item["id"])

        for item in BUILTIN_CARDS:
            card = db.query(WritingCard).filter(WritingCard.id == item["id"]).first()
            if card is None:
                db.add(
                    WritingCard(
                        id=item["id"],
                        name=item["name"],
                        writing_guide_ids=item["writing_guide_ids"],
                        style_ids=item["style_ids"],
                        reference_ids=item["reference_ids"],
                        continuation_ids=item["continuation_ids"],
                        extra_requirements=item.get("extra_requirements"),
                        builtin=True,
                    )
                )
        db.commit()
    finally:
        db.close()

    if need_index:
        import threading

        def _index_all():
            from services.rag_service import index_source

            for sid in need_index:
                try:
                    index_source(sid)
                except Exception as e:
                    print(f"[Builtin] index {sid} failed: {e}")

        threading.Thread(target=_index_all, daemon=True).start()
