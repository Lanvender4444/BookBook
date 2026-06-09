# BookBook - An AI eBook Generator

## Quick Start
### Configure Environment Variables
```
cd backend
copy .env.example .env
```

### Install Backend Dependencies with uv

```
cd backend

# Sync and install all dependencies (automatically creates virtual environment)
uv sync

# Or specify Python version
uv sync --python 3.11
```

### Initialize Database
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Start Backend Service
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Note: `uv run` automatically uses Python from the project's virtual environment, no manual activation needed.

Backend will run at http://localhost:8000

API documentation: http://localhost:8000/docs

### Install Frontend Dependencies
```
cd frontend
npm install
```

### Start Frontend Development Server

```
cd frontend
npm run dev
```
Frontend will run at http://localhost:5173

## Quick Launch Scripts (Windows)

### One-Click Start Backend

Create `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### One-Click Start Frontend

Create `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### One-Click Start All Services

Create `start_all.bat`:
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

## Docker Deployment (Optional)

If using Docker, ensure Docker Desktop is installed, then run:

```bash
docker-compose up -d
```

This will start both frontend and backend services.

**Note:** Environment variables must be configured in `backend/.env` first.


## Supported Languages

BookBook supports the following interface languages:

| Language | Code | Language | Code |
|------|------|------|------|
| Chinese (Simplified) | zh-CN | Chinese (Traditional) | zh-TW |
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

Total of **82** supported languages.

## Port Description

| Service | Port | Description |
|------|------|------|
| Frontend (Vite) | 5173 | React development server |
| Backend (FastAPI) | 8000 | API service |
| P2P Broadcast (UDP) | 47832 | LAN node discovery |
| P2P Book Sync (TCP) | 47833 | Book data transfer |

**Firewall Settings:**
If using P2P features, ensure ports 47832 (UDP) and 47833 (TCP) are open on your LAN.
