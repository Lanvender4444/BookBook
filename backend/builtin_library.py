"""内置知识库：风格库 / 写作指导 的预置条目 + 默认写作卡。

内容以 Python 常量存储（而非数据文件），这样 PyInstaller --onefile 打包零配置。
要新增内置条目，往 BUILTIN_SOURCES / BUILTIN_CARDS 里加 dict 即可，
id 必须以 "builtin-" 开头且全局唯一；应用启动时自动种子化（已存在则更新内容）。

每个 source: {id, name, category, content, prompt, language(可选)}
category: writing_guide | style | reference | continuation
每个 card: {id, name, tags, *_ids, extra_requirements}
"""

BUILTIN_SOURCES = [
    # ---------------- 风格库 ----------------
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
    {
        "id": "builtin-style-hardboiled",
        "name": "硬汉派叙事",
        "category": "style",
        "prompt": "模仿钱德勒式硬汉派文风：冷峻克制的第一人称，简短有力，比喻辛辣。",
        "content": (
            "「硬汉派」风格样本：\n\n"
            "雨下了三天，城市像一块泡烂的海绵。她走进我办公室的时候，"
            "带着一身湿气和一个显然不打算说实话的故事。我给自己倒了杯威士忌，没给她倒——"
            "我的酒只招待诚实的人，所以大部分时候我一个人喝。\n\n"
            "这种风格的要点：\n"
            "1. 第一人称，叙述者见惯世故、自嘲但有原则。\n"
            "2. 短句为主，动词强劲，形容词吝啬。\n"
            "3. 比喻出人意料且带刺：把抽象情绪钉在具体事物上。\n"
            "4. 对话占比高，话里有话，没人把真话一次说完。"
        ),
    },
    {
        "id": "builtin-style-academic",
        "name": "学术严谨",
        "category": "style",
        "prompt": "模仿学术写作风格：论证严密、术语准确、立场克制，区分事实与观点。",
        "content": (
            "「学术严谨」风格样本：\n\n"
            "现有研究普遍认为该机制由两个因素共同驱动，但二者的相对贡献仍存在争议。"
            "一方面，早期实证工作表明因素A在多数情境下占主导地位；另一方面，"
            "近期的对照实验提示，在控制样本偏差后，因素B的效应量显著上升。"
            "因此，更稳妥的结论是：二者的作用高度依赖于边界条件，而非简单的主次关系。\n\n"
            "这种风格的要点：\n"
            "1. 每个论断都给出依据或标注其确定性程度（普遍认为/有证据表明/仍有争议）。\n"
            "2. 主动呈现对立观点，再给出权衡后的判断。\n"
            "3. 概念第一次出现时给出精确定义，全文用词一致。\n"
            "4. 避免夸张修辞与绝对化表述。"
        ),
    },
    {
        "id": "builtin-style-fairytale",
        "name": "童话叙事",
        "category": "style",
        "prompt": "模仿经典童话文风：温暖、有韵律感、适合朗读，蕴含朴素的道理。",
        "content": (
            "「童话叙事」风格样本：\n\n"
            "在很远很远的山谷里，住着一只不会冬眠的小熊。别的熊都说：“睡吧睡吧，"
            "冬天没有什么好看的。”可小熊偏偏想知道，雪落在松枝上的声音是什么样子。"
            "于是它裹上奶奶织的红围巾，踩着咯吱咯吱的雪，一步一步走进了银白色的森林。\n\n"
            "这种风格的要点：\n"
            "1. 开头用“在很久以前/在很远的地方”式的经典句式建立距离感。\n"
            "2. 重复与排比制造韵律，适合朗读。\n"
            "3. 把抽象品质（勇气、好奇心）落在具体小物件上（红围巾、小灯笼）。\n"
            "4. 道理藏在故事里，绝不直接说教。"
        ),
    },
    # ---------------- 写作指导 ----------------
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
    {
        "id": "builtin-guide-story",
        "name": "小说叙事指导（冲突驱动）",
        "category": "writing_guide",
        "prompt": "按本指导推进小说情节，确保每章有冲突与变化。",
        "content": (
            "小说叙事写作指导：\n\n"
            "1. 每一章必须包含至少一个冲突（外部冲突或内心冲突），章末人物处境或认知必须发生变化。\n"
            "2. 遵循「目标 → 障碍 → 抉择 → 后果」的场景结构；后果引出下一场景的目标。\n"
            "3. 「呈现而非陈述」原则：用动作、对话和细节呈现情绪，不直接报告人物感受。\n"
            "4. 对话要承担双重功能：推进情节 + 暴露性格；删掉一切寒暄式对白。\n"
            "5. 每章结尾留一个钩子：未解的问题、新的威胁或反转的迹象。\n"
            "6. 人物弧线全书一致：开篇建立缺陷，中段被冲突逼到极限，结尾完成（或彻底拒绝）转变。"
        ),
    },
    {
        "id": "builtin-guide-tutorial",
        "name": "教程类指导（循序渐进）",
        "category": "writing_guide",
        "prompt": "按本指导编写教程内容，保证可操作性。",
        "content": (
            "教程类写作指导：\n\n"
            "1. 先讲“为什么”，再讲“是什么”，最后讲“怎么做”。\n"
            "2. 知识点按依赖关系排序：后一章只能依赖前面讲过的概念。\n"
            "3. 每个知识点配最小可行示例，并预告常见错误及排查方法。\n"
            "4. 每章末尾设置 2-3 个由浅入深的练习，第一题必须是对正文示例的直接复现。\n"
            "5. 控制认知负荷：一章只引入 3 个以内的新概念。"
        ),
    },
]

# 默认写作卡（组合内置知识源；可在界面里复制后改造）
BUILTIN_CARDS = [
    {
        "id": "builtin-card-popsci",
        "name": "科普写作（深入浅出）",
        "tags": ["科普", "非虚构"],
        "writing_guide_ids": ["builtin-guide-structure"],
        "style_ids": ["builtin-style-shenrujianchu"],
        "reference_ids": [],
        "continuation_ids": [],
        "extra_requirements": "面向零基础读者，避免堆砌术语；必要的术语第一次出现时给出通俗解释。",
    },
    {
        "id": "builtin-card-novel-jazz",
        "name": "爵士乐时代小说",
        "tags": ["小说", "文学"],
        "writing_guide_ids": ["builtin-guide-story"],
        "style_ids": ["builtin-style-jazz-age"],
        "reference_ids": [],
        "continuation_ids": [],
        "extra_requirements": "时代背景为1920年代美国；注重氛围描写与人物幻灭感。",
    },
    {
        "id": "builtin-card-detective",
        "name": "硬汉侦探小说",
        "tags": ["小说", "悬疑"],
        "writing_guide_ids": ["builtin-guide-story"],
        "style_ids": ["builtin-style-hardboiled"],
        "reference_ids": [],
        "continuation_ids": [],
        "extra_requirements": "第一人称叙事；每章埋一条线索，最终解答必须在前文有公平铺垫。",
    },
    {
        "id": "builtin-card-tutorial",
        "name": "技术教程",
        "tags": ["教程", "技术"],
        "writing_guide_ids": ["builtin-guide-tutorial", "builtin-guide-structure"],
        "style_ids": ["builtin-style-shenrujianchu"],
        "reference_ids": [],
        "continuation_ids": [],
        "extra_requirements": "示例代码要完整可运行；每章末尾附练习题。",
    },
    {
        "id": "builtin-card-academic",
        "name": "学术综述",
        "tags": ["学术", "非虚构"],
        "writing_guide_ids": ["builtin-guide-structure"],
        "style_ids": ["builtin-style-academic"],
        "reference_ids": [],
        "continuation_ids": [],
        "extra_requirements": "区分既有共识与开放争议；重要论断标注确定性程度。",
    },
    {
        "id": "builtin-card-children",
        "name": "儿童故事",
        "tags": ["童话", "儿童"],
        "writing_guide_ids": ["builtin-guide-story"],
        "style_ids": ["builtin-style-fairytale"],
        "reference_ids": [],
        "continuation_ids": [],
        "extra_requirements": "适合6-10岁儿童；语言简单温暖，无暴力恐怖内容；每章结尾给一个温柔的小悬念。",
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
                        tags=item.get("tags", []),
                        builtin=True,
                    )
                )
            else:
                # 内置卡内容随版本刷新
                card.name = item["name"]
                card.writing_guide_ids = item["writing_guide_ids"]
                card.style_ids = item["style_ids"]
                card.reference_ids = item["reference_ids"]
                card.continuation_ids = item["continuation_ids"]
                card.extra_requirements = item.get("extra_requirements")
                card.tags = item.get("tags", [])
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
