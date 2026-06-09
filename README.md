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


## 支持语言

BookBook 支持以下语言的界面显示：

| 语言 | 代码 | 语言 | 代码 |
|------|------|------|------|
| 中文（简体） | zh-CN | 中文（繁體） | zh-TW |
| 日本語 | ja | 한국어 | ko |
| English | en | Deutsch | de |
| français | fr | français (Canada) | fr-CA |
| español | es | español (Latinoamérica) | es-419 |
| español (México) | es-MX | italiano | it |
| português (Brasil) | pt-BR | português (Portugal) | pt-PT |
| Русский | русский | українська | uk |
| беларуская | be | български | bg |
| čeština | cs | dansk | da |
| eesti | et | ελληνικά | el |
| suomi | fi | galego | gl |
| hrvatski | hr | magyar | hu |
| íslenska | is | latviešu | lv |
| lietuvių | lt | macedonian | mk |
| Nederlands | nl | norsk bokmål | nb |
| norsk nynorsk | nn | polski | pl |
| română | ro | shqip | sq |
| slovenčina | sk | slovenščina | sl |
| srpski | sr | svenska | sv |
| Türkçe | tr | català | ca |
| Cebuano | ceb | creole haïtien | ht |
| euskara | eu | Filipino | fil |
| Indonesia | id | Jawa | jv |
| Melayu | ms | Tiếng Việt | vi |
| Afrikaans | af | azərbaycan | az |
| ქართული | ka | հայերեն | hy |
| Kiswahili | sw | Latin | la |
| العربية | ar | العربية (العامية المصرية) | ar-EG |
| فارسی | fa | پښتو | ps |
| سنڌي | sd | اردو | ur |
| አማርኛ | am | বাংলা | bn |
| ਪੰਜਾਬੀ | pa | ગુજરાતી | gu |
| ଓଡ଼ିଆ | or | தமிழ் | ta |
| తెలుగు | te | ಕನ್ನಡ | kn |
| മലയാളം | ml | සිංහල | si |
| ไทย | th | मराठी | mr |
| मैथिली | mai | हिन्दी | hi |
| कोंकणी | kok | नेपाली | ne |
| मैथिली | mai | မြန်မာ | my |

共支持 **82** 种语言。

## 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 (Vite) | 5173 | React 开发服务器 |
| 后端 (FastAPI) | 8000 | API 服务 |
| P2P 广播 (UDP) | 47832 | 局域网节点发现 |
| P2P 书籍同步 (TCP) | 47833 | 书籍数据传输 |

**防火墙设置：**
如需使用 P2P 功能，请确保端口 47832（UDP）和 47833（TCP）在局域网内开放。
