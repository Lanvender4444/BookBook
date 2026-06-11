# BookBook 打包指南

## 前置要求

| 工具 | 版本要求 | 用途 |
|------|----------|------|
| Node.js | >= 18 | 前端构建 |
| Rust | >= 1.77.2 | Tauri 编译（`rustc --version` 验证） |
| Python | >= 3.11 | 后端打包 |
| PyInstaller | >= 6.0 | Python 打包为 exe（`pip install pyinstaller`） |

## 端口配置

项目根目录 `config.json` 定义了端口，打包时需确保一致：

```json
{
  "backend_port": 18140,
  "frontend_port": 17983,
  "p2p_port": 47833
}
```

前端通过 `vite.config.js` 读取此文件注入 `__BACKEND_PORT__`，后端通过 `sys.frozen` 判断运行模式读取同文件。

---

## 第一步：打包 Python 后端

使用 `backend/.venv` 虚拟环境打包，确保依赖完整：

```powershell
cd backend
.\.venv\Scripts\activate
pyinstaller --onefile --noconsole --name backend main.py
```

产出文件：`backend/dist/backend.exe`

> `main.py` 已内置 `sys.frozen` 检测，打包后会自动在 exe 同级目录查找 `config.json`。

## 第二步：复制 backend.exe 到 Tauri binaries 目录

Tauri sidecar 要求文件名带 target triple 后缀：

```powershell
# 查询当前系统 triple
$TRIPLE = (rustc -vV | Select-String "host:" | ForEach-Object { ($_ -split " ")[1] }).Trim()

# 创建目录（如不存在）
New-Item -ItemType Directory -Force -Path "frontend\src-tauri\binaries"

# 复制并重命名
Copy-Item -Path "backend\dist\backend.exe" -Destination "frontend\src-tauri\binaries\backend-$TRIPLE.exe" -Force
```

Windows 上 `TRIPLE` 通常是 `x86_64-pc-windows-msvc`，最终文件名为：
`frontend/src-tauri/binaries/backend-x86_64-pc-windows-msvc.exe`

## 第三步：构建 Tauri 桌面应用

```powershell
cd frontend
npm install
npx tauri build
```

此命令自动执行：`npm run build`（前端） → Rust 编译 → 打包

产出文件位于：

| 类型 | 路径 |
|------|------|
| 独立 exe | `frontend/src-tauri/target/release/app.exe` |
| NSIS 安装包 | `frontend/src-tauri/target/release/bundle/nsis/BookBook_0.1.0_x64-setup.exe` |
| MSI 安装包 | `frontend/src-tauri/target/release/bundle/msi/BookBook_0.1.0_x64_en-US.msi` |

## 开发模式

```powershell
# 终端1：启动后端
cd backend
.\.venv\Scripts\activate
python main.py

# 终端2：启动前端开发服务器
cd frontend
npm run dev
```

Tauri 开发模式：

```powershell
cd frontend
npx tauri dev
```

> `tauri dev` 会自动启动前端 dev server 和 Rust 编译，sidecar 后端需手动启动或等 `tauri dev` 自动拉起。

---

## 目录结构

```
BookBook/
├── config.json                          # 端口配置（打包进 exe 同级目录）
├── backend/
│   ├── main.py                          # FastAPI 入口（支持 sys.frozen 模式）
│   ├── config.py                        # 配置（支持 sys.frozen 模式）
│   ├── database.py                      # 数据库（支持 sys.frozen 模式）
│   ├── .venv/                           # Python 虚拟环境
│   └── dist/backend.exe                 # PyInstaller 产出
├── frontend/
│   ├── src/                             # React 前端源码
│   ├── dist/                            # 前端构建产出
│   ├── vite.config.js                   # Vite 配置（读取 config.json 端口）
│   └── src-tauri/
│       ├── Cargo.toml                   # Rust 依赖
│       ├── tauri.conf.json              # Tauri 配置（sidecar、窗口等）
│       ├── capabilities/default.json    # sidecar 权限
│       ├── src/lib.rs                   # Rust 主进程（启动 sidecar）
│       ├── src/main.rs                  # Rust 入口
│       ├── binaries/
│       │   └── backend-x86_64-pc-windows-msvc.exe  # Python sidecar
│       └── target/release/bundle/       # 打包产物
```

## 注意事项

1. **Sidecar 自动管理**：Tauri 启动时自动拉起 `backend.exe`，窗口关闭时自动 kill，无需手动管理进程。
2. **config.json 必须存在**：打包后在 exe 同级目录放置 `config.json`，后端和前端都依赖它。`tauri.conf.json` 的 `bundle.resources` 已配置将根目录 `config.json` 打包进去。
3. **数据目录**：数据库文件保存在 `exe 同级目录/data/` 下（`database.py` 通过 `sys.frozen` 判断路径）。
4. **冷启动等待**：Python 后端冷启动约 1-2 秒，前端 `useBackendReady` hook 会轮询 `/api/identity` 直到后端就绪才渲染 UI。
5. **重新打包 Python 后端时**：每次修改 `backend/` 代码后需重新执行第一步和第二步，然后重新 `npx tauri build`，否则 sidecar 仍是旧版本。
6. **首次 Rust 编译较慢**：约 5-10 分钟，后续增量编译只需 1-2 分钟。