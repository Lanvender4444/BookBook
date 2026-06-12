# 写作卡 & RAG 知识库

## 概念

**知识源**（四类，均为「文档内容 + 配套 prompt」）：

| 分类 | 用途 |
|------|------|
| 写作指导 writing_guide | 约束写法/结构（如"总-分-总章节结构"） |
| 风格库 style | 模仿文风（内置示例："深入浅出"、"美国爵士乐时代风格"） |
| 资料库 reference | 提供事实依据，生成时优先采用 |
| 续写 continuation | 根据所投文章生成其后续内容（自动携带文章结尾上下文以保证衔接） |

投递方式：上传文件（复制托管）、链接本地文件（引用原路径，类似软链接）、粘贴纯文本。
支持格式：txt / md / pdf / docx / epub。

**写作卡** = 写作指导 + 风格库 + 资料库 + 续写 + 额外需求，五部分自由组合，可自建/复制/编辑。
生成页选中写作卡后，大纲与每一章会按当前内容自动检索相关片段注入 prompt。

## 检索机制

- 已配置支持 embedding 的厂商（OpenAI/智谱/通义/Gemini/SiliconFlow/Mistral 等）→ 向量检索（存 SQLite）
- 厂商无 embedding 接口（如 Anthropic/DeepSeek）或调用失败 → 自动降级为 BM25 关键词检索（完全离线）
- 状态在「写作卡 → 知识库」页可见：已索引(向量) / 已索引(关键词) / 失败（可重建索引）

## 语言一致性

所有生成 prompt 注入「语言铁律」：全书强制使用所选语言，参考资料为其他语言时必须转写；
唯一例外是语言教学类书籍，允许"本语言 + 目标语言"对照，讲解仍用本语言。
章节生成现在也显式传入语言（此前只有大纲有语言约束，是跳语言 bug 的根源）。

## 内置库扩展

内置风格/指导/写作卡定义在 `backend/builtin_library.py` 的 `BUILTIN_SOURCES` / `BUILTIN_CARDS`，
id 以 `builtin-` 开头，启动时自动种子化并建索引；改完内容重启后端即生效（内容变更会自动重建索引）。

## 相关 API

- `GET/POST/PATCH/DELETE /api/knowledge/sources*`（upload / link / text 三种投递）
- `POST /api/knowledge/sources/{id}/reindex`、`POST /api/knowledge/search`（调试检索）
- `GET/POST/PUT/DELETE /api/knowledge/cards*`、`POST /api/knowledge/cards/{id}/duplicate`
- `POST /api/generate/stream` 新增 `card_id`、`extra_requirements` 字段
