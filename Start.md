# 📚 AI eBook Generator + P2P 书库 — 项目启动文档

## 项目概述

一个本地优先的 AI 电子书生成平台，用户可以通过自然语言描述需求，由 LLM 自动生成完整电子书，并通过 P2P 网络与其他用户共享书籍。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + Vite + TailwindCSS |
| 后端 | Python 3.11 + FastAPI |
| 数据库 | SQLite (via SQLAlchemy) |
| LLM | Anthropic Claude API (claude-sonnet-4) |
| P2P | libp2p (py-libp2p) 或 自实现 TCP/UDP 节点发现 |

---

## 目录结构

```
ebook-generator/
├── backend/
│   ├── main.py                  # FastAPI 入口
│   ├── config.py                # 配置（API Key、端口等）
│   ├── database.py              # SQLite 初始化 & ORM
│   ├── models.py                # SQLAlchemy 数据模型
│   ├── routers/
│   │   ├── books.py             # 书籍 CRUD 接口
│   │   ├── generate.py          # LLM 生成接口（SSE 流式）
│   │   └── p2p.py               # P2P 节点接口
│   ├── services/
│   │   ├── llm_service.py       # Anthropic API 封装
│   │   ├── book_builder.py      # 大纲→章节 生成逻辑
│   │   ├── identity.py          # 用户 ID 生成（MAC + hash）
│   │   └── p2p_service.py       # P2P 节点发现 & 书籍同步
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Generate.jsx     # 生成页：输入需求，流式展示进度
│   │   │   ├── Library.jsx      # 我的书库
│   │   │   ├── Reader.jsx       # 书籍阅读器
│   │   │   └── Network.jsx      # P2P 网络 & 收到的书
│   │   ├── components/
│   │   │   ├── BookCard.jsx
│   │   │   ├── OutlineTree.jsx  # 大纲预览组件
│   │   │   ├── ProgressBar.jsx  # 章节生成进度
│   │   │   └── PeerList.jsx     # 在线节点列表
│   │   ├── store/               # Zustand 状态管理
│   │   ├── api.js               # 后端 API 封装
│   │   └── App.jsx
│   ├── index.html
│   └── package.json
│
├── data/
│   └── ebooks.db                # SQLite 数据库文件
│
├── Start.md                     # 本文件
└── docker-compose.yml           # 可选：容器化部署
```

---

## 核心功能模块

### 1. 用户身份系统

```python
# backend/services/identity.py
import hashlib
import uuid
import getmac  # pip install getmac

def generate_user_id() -> str:
    mac = getmac.get_mac_address() or "00:00:00:00:00:00"
    machine_id = str(uuid.getnode())
    raw = f"{mac}-{machine_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
```

- 基于 MAC 地址 + 机器 UUID，SHA-256 哈希取前 16 位
- 本地唯一，无需服务器注册
- 首次运行写入 SQLite，后续复用

---

### 2. LLM 电子书生成流程

```
用户输入需求
    │
    ▼
[Step 1] 生成大纲 （此处也有前端输入界面，输入要求，例如：难易度，文字量，等等）
    └─ Prompt: 根据需求生成 JSON 格式大纲（标题、简介、章节列表）
    │
    ▼
[Step 2] 逐章节生成内容（并发或顺序）
    └─ 每章独立调用 LLM，携带大纲上下文
    │
    ▼
[Step 3] 组装电子书 → 存入 SQLite
    └─ 返回 book_id，前端跳转阅读器
```

**SSE 流式推送进度：**

```python
# backend/routers/generate.py
@router.post("/generate/stream")
async def generate_stream(request: GenerateRequest):
    async def event_generator():
        # Step 1: 大纲
        outline = await llm_service.generate_outline(request.prompt)
        yield f"data: {json.dumps({'type': 'outline', 'data': outline})}\n\n"

        # Step 2: 逐章生成
        chapters = []
        for i, chapter in enumerate(outline['chapters']):
            content = await llm_service.generate_chapter(outline, chapter, i)
            chapters.append(content)
            yield f"data: {json.dumps({'type': 'chapter', 'index': i, 'data': content})}\n\n"

        # Step 3: 保存
        book_id = await book_builder.save(outline, chapters, request.user_id)
        yield f"data: {json.dumps({'type': 'done', 'book_id': book_id})}\n\n"

    return EventSourceResponse(event_generator())
```

---

### 3. SQLite 数据模型

```python
# backend/models.py
class Book(Base):
    __tablename__ = "books"
    id            = Column(String, primary_key=True)   # UUID
    title         = Column(String, nullable=False)
    description   = Column(Text)
    outline       = Column(JSON)                        # 大纲 JSON
    created_at    = Column(DateTime, default=func.now())
    author_id     = Column(String)                      # 本地用户 ID
    source        = Column(String, default="local")     # local / p2p
    peer_origin   = Column(String, nullable=True)       # 来源节点 ID

class Chapter(Base):
    __tablename__ = "chapters"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    book_id       = Column(String, ForeignKey("books.id"))
    index         = Column(Integer)
    title         = Column(String)
    content       = Column(Text)
```

---

### 4. P2P 网络模块

**方案：基于 UDP 广播（局域网）+ 可选公网中继**

```
节点 A                        节点 B
  │                              │
  │── UDP 广播（局域网发现）──►  │
  │◄─ 响应（节点ID、书单摘要）── │
  │                              │
  │── TCP 请求特定书籍 ────────► │
  │◄─ 书籍 JSON 数据流 ───────── │
  │                              │
  存入 SQLite (source=p2p)
```

```python
# backend/services/p2p_service.py
import asyncio, socket, json

BROADCAST_PORT = 47832
BOOK_SHARE_PORT = 47833

class P2PService:
    def __init__(self, user_id: str, db):
        self.user_id = user_id
        self.db = db
        self.peers = {}  # {peer_id: (ip, port)}

    async def start(self):
        await asyncio.gather(
            self.broadcast_loop(),    # 每30秒广播自己
            self.listen_broadcast(),  # 监听其他节点
            self.serve_books(),       # 提供书籍下载服务
        )

    async def broadcast_loop(self):
        # 广播 {user_id, book_count, port}
        ...

    async def sync_book(self, peer_ip: str, book_id: str):
        # TCP 拉取书籍数据
        ...
```

**公网支持（可选）：** 使用 WebSocket 中继服务器或 libp2p 的 DHT 节点发现。

---

## 数据库初始化

```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "sqlite:///./data/ebooks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
```

---

## API 接口总览

### 书籍生成
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/generate/stream` | SSE 流式生成电子书 |
| GET  | `/api/generate/status/{id}` | 查询生成状态 |

### 书库
| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/api/books` | 获取所有书籍（本地+P2P） |
| GET  | `/api/books/{id}` | 获取书籍详情 |
| DELETE | `/api/books/{id}` | 删除书籍 |
| GET  | `/api/books/{id}/export` | 导出为 Markdown/EPUB |

### P2P
| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/api/peers` | 在线节点列表 |
| POST | `/api/peers/{peer_id}/sync` | 从节点拉取书单 |
| POST | `/api/peers/{peer_id}/books/{book_id}` | 下载特定书籍 |

### 身份
| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/api/identity` | 获取本地用户 ID |

---

## 前端页面规划

### 生成页 `/generate`
- 文本区域输入需求
- 实时显示大纲树（生成中动画）
- 章节进度条（X/N 章已完成）
- 完成后"去阅读"按钮

### 书库页 `/library`
- 书架网格布局
- 本地书 / P2P 来源书 Tab 切换
- 书籍卡片：封面色块 + 标题 + 章节数 + 来源标记

### 阅读器页 `/reader/:id`
- 左侧大纲导航
- 右侧 Markdown 渲染内容
- 支持导出

### 网络页 `/network`
- 在线节点列表（节点ID + 书籍数量）
- 点击节点查看其书单
- 一键接收书籍

---

## 快速启动

### 1. 克隆 & 安装依赖

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 2. 配置环境变量

```bash
# backend/.env
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-4-20250514
P2P_ENABLED=true
P2P_BROADCAST_PORT=47832
P2P_BOOK_PORT=47833
```

### 3. 初始化数据库

```bash
cd backend
python -c "from database import init_db; init_db()"
```

### 4. 启动服务

```bash
# 终端 1：后端
cd backend && uvicorn main:app --reload --port 8000

# 终端 2：前端
cd frontend && npm run dev
```

访问 `http://localhost:5173`

---

## 依赖清单

### backend/requirements.txt
```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
sqlalchemy>=2.0.0
anthropic>=0.28.0
sse-starlette>=1.8.0
getmac>=0.9.0
python-dotenv>=1.0.0
aiofiles>=23.0.0
pydantic>=2.0.0
```

### frontend/package.json（关键依赖）
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-router-dom": "^6.23.0",
    "zustand": "^4.5.0",
    "react-markdown": "^9.0.0",
    "tailwindcss": "^3.4.0",
    "eventsource-parser": "^1.1.0"
  }
}
```

---

## 开发路线图

```
Phase 1（Week 1-2）：核心生成
  ✅ FastAPI 基础架构
  ✅ SQLite 模型 + 初始化
  ✅ LLM 大纲生成
  ✅ LLM 章节逐步生成 + SSE
  ✅ 前端生成页 + 进度展示

Phase 2（Week 3）：书库 & 阅读
  ✅ 书库 CRUD 接口
  ✅ 前端书库页
  ✅ Markdown 阅读器
  ✅ Markdown / EPUB 导出

Phase 3（Week 4）：P2P 网络
  ✅ 用户身份 ID 生成
  ✅ UDP 节点广播发现
  ✅ TCP 书籍同步
  ✅ 前端网络页

Phase 4（优化）：
  ⬜ 封面自动生成（色彩派生）
  ⬜ 公网 P2P 中继支持
  ⬜ 书籍版本控制（哈希校验）
  ⬜ 分类 / 标签 / 搜索
```

---

## 注意事项

1. **API Key 安全**：`.env` 文件加入 `.gitignore`，不要提交密钥
2. **P2P 防火墙**：确保 47832（UDP）和 47833（TCP）端口在局域网内开放
3. **SQLite 并发**：FastAPI 异步环境下使用 `check_same_thread=False` + 连接池
4. **LLM 成本控制**：章节生成建议限制 `max_tokens=4096`，大书分批生成
5. **P2P 内容安全**：接收 P2P 书籍前校验 JSON schema，防止恶意数据注入

---

*文档版本：v1.0 | 生成日期：2026-06-08*
