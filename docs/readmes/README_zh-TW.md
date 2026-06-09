# BookBook - AI電子書產生器

## 快速開始
### 設定環境變數
```
cd backend
copy .env.example .env
```

### 使用 uv 安裝後端依賴

```
cd backend

# 同步安裝所有依賴（自動建立虛擬環境）
uv sync

# 或指定 Python 版本
uv sync --python 3.11
```

### 初始化資料庫
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### 啟動後端服務
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
說明：`uv run` 會自動使用專案虛擬環境中的 Python 執行命令，無需手動啟動環境。

後端將運行在 http://localhost:8000

API 文件位址：http://localhost:8000/docs

### 安裝前端依賴
```
cd frontend
npm install
```

### 啟動前端開發伺服器

```
cd frontend
npm run dev
```
前端將運行在 http://localhost:5173

## 快速啟動腳本（Windows）

### 一鍵啟動後端

建立 `start_backend.bat`：
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### 一鍵啟動前端

建立 `start_frontend.bat`：
```batch
@echo off
cd frontend
npm run dev
pause
```

### 一鍵啟動全部服務

建立 `start_all.bat`：
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

## Docker 部署（選擇性）

如果使用 Docker，請確認已安裝 Docker Desktop，然後執行：

```bash
docker-compose up -d
```

這將同時啟動前後端服務。

**注意：** 需要先在 `backend/.env` 中設定好環境變數。


## 支援語言

BookBook 支援以下介面語言：

| 語言 | 代碼 | 語言 | 代碼 |
|------|------|------|------|
| 中文（簡體） | zh-CN | 中文（繁體） | zh-TW |
| 日本語 | ja | 한국어 | ko |
| English | en | Deutsch | de |
| Français | fr | Français (Canada) | fr-CA |
| Español | es | Español (Latinoamérica) | es-419 |
| Español (México) | es-MX | Italiano | it |
| Português (Brasil) | pt-BR | Português (Portugal) | pt-PT |
| Русский | ru | Українська | uk |
| Беларуская | be | Български | bg |
| Čeština | cs | Dansk | da |
| Eesti | et | Ελληνικά | el |
| Suomi | fi | Galego | gl |
| Hrvatski | hr | Magyar | hu |
| Íslenska | is | Latviešu | lv |
| Lietuvių | lt | Macedonian | mk |
| Nederlands | nl | Norsk bokmål | nb |
| Norsk nynorsk | nn | Polski | pl |
| Română | ro | Shqip | sq |
| Slovenčina | sk | Slovenščina | sl |
| Srpski | sr | Svenska | sv |
| Türkçe | tr | Català | ca |
| Cebuano | ceb | Creole haïtien | ht |
| Euskara | eu | Filipino | fil |
| Indonesia | id | Jawa | jv |
| Melayu | ms | Tiếng Việt | vi |
| Afrikaans | af | Azərbaycan | az |
| ქართული | ka | Հայերեն | hy |
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

共支援 **82** 種語言。

## 埠說明

| 服務 | 埠 | 說明 |
|------|------|------|
| 前端 (Vite) | 5173 | React 開發伺服器 |
| 後端 (FastAPI) | 8000 | API 服務 |
| P2P 廣播 (UDP) | 47832 | 區域網路節點發現 |
| P2P 書籍同步 (TCP) | 47833 | 書籍資料傳輸 |

**防火牆設定：**
如需使用 P2P 功能，請確保埠 47832（UDP）和 47833（TCP）在區域網路內開放。
