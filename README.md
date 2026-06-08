# BookBook - An AI eBook Generator

## 快速开始
### 配置环境变量
```
cd backend
copy .env.example .env
```

### 使用 uv 安装后端依赖

```
cd backend

# 同步安装所有依赖（自动创建虚拟环境）
uv sync

# 或指定 Python 版本
uv sync --python 3.11
```

### 初始化数据库
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### 启动后端服务
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
说明： uv run 会自动使用项目虚拟环境中的 Python 运行命令，无需手动激活环境。

后端将运行在 http://localhost:8000

API 文档地址： http://localhost:8000/docs

### 安装前端依赖
```
cd frontend
npm install
```

### 启动前端开发服务器

```
cd frontend
npm run dev
```
前端将运行在 http://localhost:5173

## 快速启动脚本（Windows）

### 一键启动后端

创建 `start_backend.bat`：
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### 一键启动前端

创建 `start_frontend.bat`：
```batch
@echo off
cd frontend
npm run dev
pause
```

### 一键启动全部服务

创建 `start_all.bat`：
```batch
@echo off
echo Starting backend...
start "Backend" cmd /k "cd backend && uv run uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Services started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
pause
```

---

## Docker 部署（可选）

如果使用 Docker，确保已安装 Docker Desktop，然后运行：

```bash
docker-compose up -d
```

这将同时启动前后端服务。

**注意：** 需要先在 `backend/.env` 中配置好环境变量。


## 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 (Vite) | 5173 | React 开发服务器 |
| 后端 (FastAPI) | 8000 | API 服务 |
| P2P 广播 (UDP) | 47832 | 局域网节点发现 |
| P2P 书籍同步 (TCP) | 47833 | 书籍数据传输 |

**防火墙设置：**
如需使用 P2P 功能，请确保端口 47832（UDP）和 47833（TCP）在局域网内开放。
