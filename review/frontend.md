# BookBook 前端结构详细拆解

## 一、技术栈概览

| 技术 | 版本 | 用途 |
|------|------|------|
| React | ^18.3.0 | UI 框架 |
| Vite | ^5.3.0 | 构建工具 / 开发服务器 |
| Tailwind CSS | ^3.4.4 | 原子化 CSS 框架 |
| React Router DOM | ^6.23.0 | 客户端路由 |
| Zustand | ^4.5.0 | 全局状态管理 |
| React Markdown | ^9.0.0 | Markdown 渲染 |
| Highlight.js | ^11.11.1 | 代码高亮 |
| eventsource-parser | ^1.1.0 | SSE 流解析 |

---

## 二、目录结构

```
frontend/
├── index.html              # HTML 入口（单页应用）
├── vite.config.js          # Vite 配置（含代理）
├── tailwind.config.js      # Tailwind CSS 配置
├── postcss.config.js       # PostCSS 配置
├── package.json            # 依赖定义
├── public/                 # 静态资源
│   └── icon.png            # 应用图标
├── src/
│   ├── main.jsx            # 应用入口（React 挂载）
│   ├── App.jsx             # 根组件（路由 + 导航栏）
│   ├── index.css           # 全局样式（Tailwind 导入）
│   ├── api.js              # 统一 API 封装
│   ├── i18n/
│   │   ├── index.jsx       # 国际化 Provider + Hook
│   │   └── *.json          # 80+ 语言翻译文件
│   ├── store/
│   │   └── index.js        # Zustand 全局状态
│   ├── styles/
│   │   └── typora-reader.css # 阅读器 Typora 风格样式
│   ├── components/         # 可复用组件
│   │   ├── BookCard.jsx
│   │   ├── ConfirmModal.jsx
│   │   ├── CustomInput.jsx
│   │   ├── CustomSelect.jsx
│   │   ├── OutlineTree.jsx
│   │   ├── PeerList.jsx
│   │   ├── ProgressBar.jsx
│   │   ├── TypewriterHeading.jsx
│   │   └── TypewriterPlaceholder.jsx
│   └── pages/              # 页面级组件
│       ├── Generate.jsx
│       ├── History.jsx
│       ├── Library.jsx
│       ├── Network.jsx
│       └── Reader.jsx
```

---

## 三、核心文件详解

### 1. main.jsx — 应用入口

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

- 使用 `ReactDOM.createRoot` 创建 React 18 并发模式根节点
- 挂载点：`#root`（位于 `index.html`）
- 全局样式通过 `index.css` 引入（内含 Tailwind 指令）

---

### 2. App.jsx — 根组件

**职责：**
- 定义 5 条客户端路由
- 渲染顶部导航栏（NavBar）
- 提供全局语言切换器（LanguageSwitcher）
- 包裹 `I18nProvider` 提供国际化上下文

**路由表：**

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | `Generate` | 默认首页 |
| `/generate` | `Generate` | 电子书生成页 |
| `/history` | `History` | 生成历史记录 |
| `/library` | `Library` | 本地书库 |
| `/reader/:id` | `Reader` | Markdown 阅读器 |
| `/network` | `Network` | P2P 网络共享 |

**LanguageSwitcher：**
- 支持 88 种 UI 语言
- 搜索过滤功能
- 下拉菜单选择，持久化到 `localStorage`

---

### 3. vite.config.js — 构建配置

```js
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

- 开发服务器端口：`5173`
- `/api` 请求代理到后端 `localhost:8000`
- 生产构建输出到 `dist/`

---

### 4. api.js — API 封装层

**统一基础路径：** `/api`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/books` | 获取书籍列表 |
| GET | `/api/books/{id}` | 获取单本书详情 |
| DELETE | `/api/books/{id}` | 删除书籍 |
| GET | `/api/books/{id}/export?format=markdown` | 导出 Markdown |
| POST | `/api/generate/stream` | 开始生成（SSE） |
| GET | `/api/generate/stream/{history_id}` | 重连生成任务 |
| POST | `/api/generate/{history_id}/cancel` | 取消生成 |
| GET | `/api/generate/history` | 获取生成历史 |
| DELETE | `/api/generate/history/{id}/permanent` | 永久删除历史 |
| GET | `/api/peers` | 获取对等节点 |
| GET | `/api/peers/me` | 获取本机 P2P 信息 |
| POST | `/api/peers/connect` | 连接对等节点 |
| POST | `/api/peers/share` | 创建分享 Token |
| POST | `/api/peers/redeem` | 兑换分享 Token |
| GET | `/api/identity` | 获取用户 ID |

---

### 5. store/index.js — 全局状态 (Zustand)

```js
const useStore = create((set) => ({
  books: [],           // 书籍列表
  currentBook: null,   // 当前阅读书籍
  generating: false,    // 是否正在生成
  outline: null,        // 当前大纲
  chapters: [],        // 已生成章节
  
  setBooks, setCurrentBook, setGenerating,
  setOutline, addChapter, resetGeneration
}))
```

- 轻量级状态管理，用于跨组件共享生成状态

---

### 6. i18n/index.jsx — 国际化系统

- **动态导入：** 使用 `import.meta.glob` 加载所有 `.json` 翻译文件
- **当前支持：** 88 种语言（zh-CN, zh-TW, en, ja, ko, es, fr, de, it, pt-BR, ru, ar, hi, bn 等）
- **回退机制：** 找不到翻译时回退到简体中文
- **持久化：** `localStorage` 保存用户选择的语言
- **参数替换：** 支持 `{key}` 插值

**翻译文件命名：** `{language_code}.json`
- 示例：`zh-CN.json`, `en.json`, `ja.json`

---

## 四、组件详解

### 1. BookCard — 书籍卡片

- 展示书籍封面（渐变背景 + 📖 图标）
- 显示标题、描述、章节数
- 语言标签（如"简体中文"、"日本語"）
- 来源标签（本地 / P2P）
- 点击跳转阅读器，支持删除操作

### 2. OutlineTree — 大纲树

- 可视化展示生成大纲
- 左侧竖线 + 圆点时间线样式
- 显示章节标题和摘要

### 3. ProgressBar — 进度条

- 章节进度可视化
- 百分比显示 + 动画过渡

### 4. ConfirmModal — 确认弹窗

- 通用确认对话框
- 支持自定义标题、消息、按钮文字

### 5. CustomInput / CustomSelect

- 封装的基础表单组件
- 统一样式和交互

### 6. TypewriterHeading / TypewriterPlaceholder

- 打字机效果组件
- 用于生成页的标题和占位符动画

---

## 五、页面详解

### 1. Generate.jsx — 生成页

**核心功能：**
- 用户输入主题和生成要求（难度、字数、章节数、风格）
- 支持 URL query 参数预填充
- 调用 `/api/generate/stream` SSE 接口
- 实时展示大纲和章节生成进度
- 支持断线重连（通过 `history_id`）
- 取消生成功能

**状态管理：**
- `prompt`：用户输入主题
- `requirements`：生成参数
- `outline`：生成的大纲
- `chapters`：已生成章节内容
- `generating`：是否正在生成
- `historyId`：当前生成任务 ID

### 2. Library.jsx — 书库页

**核心功能：**
- 展示所有书籍卡片（支持本地/P2P筛选）
- 查看/设置书籍保存目录
- 删除书籍（带确认弹窗）
- 显示用户信息

**筛选选项：**
- 全部
- 本地生成
- P2P 接收

### 3. Reader.jsx — 阅读器

**核心功能：**
- Markdown 渲染（react-markdown + remark-gfm + rehype-highlight）
- 左侧目录导航（自动提取标题）
- 滚动高亮当前章节
- Typora 风格 CSS 美化
- 响应式布局（侧边栏可折叠）

**性能优化：**
- `useMemo` 缓存标题列表
- `Map` 实现 O(1) 标题查找
- `IntersectionObserver` 滚动监听
- 常量对象提到组件外

### 4. Network.jsx — P2P 网络页

**核心功能：**
- **分享 Tab：** 创建分享链接（支持单本书或全部）、管理分享 Token
- **连接 Tab：** 输入 host:port 连接对等节点、浏览对方书库
- **兑换 Tab：** 输入 Token 兑换书籍
- 显示本机 P2P 信息（user_id, host, port, public_ip）

**子功能：**
- 复制分享 URL 到剪贴板
- 下载对方书籍到本地
- 批量下载（all_books 模式）

### 5. History.jsx — 历史记录页

**核心功能：**
- 展示所有生成历史记录
- 状态筛选（全部/进行中/已完成/已失败/已删除）
- 实时轮询正在进行的任务进度
- 展开查看详情（大纲、错误信息）
- 继续生成（跳转到 Generate 页并预填充参数）
- 软删除 / 永久删除 / 清空已删除
- 搜索功能

---

## 六、样式系统

### Tailwind CSS 配置

- **扫描路径：** `./index.html`, `./src/**/*.{js,ts,jsx,tsx}`
- **无自定义主题扩展**（使用默认配置）
- **PostCSS 处理：** autoprefixer

### 全局样式 (index.css)

- `@tailwind base;`
- `@tailwind components;`
- `@tailwind utilities;`
- 自定义阅读器样式导入

### Typora 阅读器样式 (typora-reader.css)

- 模拟 Typora 编辑器的 Markdown 渲染效果
- 标题、段落、代码块、表格等详细样式定义

---

## 七、构建与部署

```bash
# 开发
npm run dev          # 启动 Vite 开发服务器 (5173)

# 生产构建
npm run build        # 输出到 dist/

# 预览
npm run preview      # 预览生产构建
```

**生产输出：**
- 所有资源打包到 `frontend/dist/`
- 包含 hashed 文件名（缓存优化）
- 可通过 Nginx / 后端静态文件服务部署

---

## 八、前端架构特点

1. **单页应用 (SPA)** — React Router 客户端路由
2. **组件化设计** — 页面拆分为独立组件，易于维护
3. **原子化 CSS** — Tailwind 快速构建 UI，无自定义 CSS 文件膨胀
4. **流式响应** — SSE 实时展示生成进度
5. **国际化就绪** — 88 种语言，动态加载翻译文件
6. **状态分离** — Zustand 管理全局状态，组件内管理局部状态
7. **性能优化** — useMemo、useCallback、常量外提、O(1) 查找
