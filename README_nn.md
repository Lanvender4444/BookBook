# BookBook - AI eBook Generator

## Rask Start
### Konfigurer Miljøvariablar
```
cd backend
copy .env.example .env
```

### Installer Backend-avhengigheter med uv

```
cd backend

# Synkroniser og installer alle avhengigheter (oppretter virtuelt miljø automatisk)
uv sync

# Eller spesifiser Python-versjon
uv sync --python 3.11
```

### Initialiser Database
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Start Backend-teneste
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Merk: `uv run` bruker automatisk Python frå prosjektet sitt virtuelle miljø, ingen manuell aktivering er nødvendig.

Backend kjem til å køyre på http://localhost:8000

API-dokumentasjon: http://localhost:8000/docs

### Installer Frontend-avhengigheter
```
cd frontend
npm install
```

### Start Frontend-utviklingstenar

```
cd frontend
npm run dev
```
Frontend kjem til å køyre på http://localhost:5173

## Raskstart-skript (Windows)

### Start Backend med eitt klikk

Opprett `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Start Frontend med eitt klikk

Opprett `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Start alle tenester med eitt klikk

Opprett `start_all.bat`:
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

## Docker-utplassering (Valfri)

Dersom du brukar Docker, sørg for at Docker Desktop er installert, og køyr deretter:

```bash
docker-compose up -d
```

Dette startar både frontend- og backend-tenester.

**Merk:** Miljøvariablar må først konfigurerast i `backend/.env`.


## Støtta Språk

BookBook støttar desse grensesnittspråka:

| Språk | Kode | Språk | Kode |
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

Totalt **82** støtta språk.

## Portskildring

| Teneste | Port | Skildring |
|------|------|------|
| Frontend (Vite) | 5173 | React-utviklingstenar |
| Backend (FastAPI) | 8000 | API-teneste |
| P2P-sending (UDP) | 47832 | LAN-nodoppdaging |
| P2P-boksynk (TCP) | 47833 | Bokdataoverføring |

**Brannmurinnstillingar:**
Dersom du brukar P2P-funksjonar, sørg for at portane 47832 (UDP) og 47833 (TCP) er opne på ditt LAN.
