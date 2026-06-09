# BookBook - AI eBook Generator

> **AI-powered eBook generator sing ngidhang sampeyan gawe eBooks apik kanthi bantuan AI.**

## Wiwitan Cepet
### Konfigurasi Variabel Lingkungan
```
cd backend
copy .env.example .env
```

### Instalasi Backend Depedensi nganggo uv

```
cd backend

# Synchronize lan instalasi kabeh depedensi (otomatis nggawe virtual environment)
uv sync

# Utawa specify versi Python
uv sync --python 3.11
```

### Inisialisasi Database
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Miwiti Backend Service
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Catetan: `uv run` otomatis nganggo Python saka virtual environment proyek, ora perlu aktivasi manual.

Backend bakal mlaku ing http://localhost:8000

Dokumentasi API: http://localhost:8000/docs

### Instalasi Frontend Depedensi
```
cd frontend
npm install
```

### Miwiti Frontend Development Server

```
cd frontend
npm run dev
```
Frontend bakal mlaku ing http://localhost:5173

## Skrip Wiwitan Cepet (Windows)

### Miwiti Backend kanthi Siji Klik

Gawe `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Miwiti Frontend kanthi Siji Klik

Gawe `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Miwiti Kabeh Service kanthi Siji Klik

Gawe `start_all.bat`:
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

## Docker Deployment (Opsional)

Yen nggunakake Docker, priksa manawa Docker Desktop wis diinstal, banjur jalur:

```bash
docker-compose up -d
```

Iki bakal miwiti frontend lan backend service.

**Catetan:** Variabel lingkungan kudu dikonfigurasi dhisik ing `backend/.env`.


## Basa sing Didhukung

BookBook ndhukung basa antarmuka ing ngisor iki:

| Basa | Kode | Basa | Kode |
|------|------|------|------|
| 中文（简体） | zh-CN | 中文（繁體） | zh-TW |
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

Kabeh **82** basa sing didhukung.

## Deskripsi Port

| Service | Port | Deskripsi |
|------|------|------|
| Frontend (Vite) | 5173 | React development server |
| Backend (FastAPI) | 8000 | API service |
| P2P Broadcast (UDP) | 47832 | Penemuan node LAN |
| P2P Book Sync (TCP) | 47833 | Transfer data buku |

**Pengaturan Firewall:**
Yen nggunakake fitur P2P, priksa manawa port 47832 (UDP) lan 47833 (TCP) mbukak ing LAN sampeyan.
