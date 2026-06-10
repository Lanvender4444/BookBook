# BookBook 打包指南

## 前置要求

- **Node.js** >= 18
- **Rust** >= 1.77.2（用于 Tauri 构建）
  - 安装方法：访问 https://rustup.rs/ 或执行 `winget install Rustlang.Rustup`
- **Python** >= 3.11
- **PyInstaller**（已安装在 Python 环境中）

## 打包步骤

### 1. 打包 Python 后端

```bash
# 在项目根目录执行
pyinstaller --onedir --noconsole --name bookbook-backend server.py
```

打包完成后，将生成的 exe 复制到 Tauri 目录：

```bash
# Windows PowerShell
Copy-Item -Path "dist/bookbook-backend/bookbook-backend.exe" -Destination "frontend/src-tauri/binaries/bookbook-backend-x86_64-pc-windows-msvc.exe" -Force
```

### 2. 构建前端

```bash
cd frontend
npm run build
```

### 3. 构建 Tauri 桌面应用

```bash
cd frontend
npm run tauri build
```

构建完成后，安装包位于：
- `frontend/src-tauri/target/release/bundle/msi/BookBook_*.msi`
- `frontend/src-tauri/target/release/bundle/nsis/BookBook_*.exe`

## 目录结构

```
BookBook/
├── frontend/          # React 前端
│   ├── src-tauri/     # Tauri 配置
│   │   ├── binaries/  # 放置 Python 后端 exe
│   │   └── src/       # Rust 源码
│   └── dist/          # 前端构建产物
├── backend/           # Python FastAPI 后端
├── server.py          # PyInstaller 入口文件
└── dist/              # PyInstaller 输出
```

## 注意事项

1. 首次打包后，后端的数据库和书籍文件会保存在用户目录下的 `BookBook` 文件夹中。
2. 如果后端需要额外依赖，确保在 Python 环境中已安装所有依赖。
3. Tauri 的 sidecar 会在应用启动时自动拉起 Python 后端进程。

## 开发模式

```bash
# 启动前端开发服务器
cd frontend
npm run tauri dev
```

这会同时启动 React 开发服务器和 Tauri 桌面应用。
