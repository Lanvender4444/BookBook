# BookBook - AI eBook Generator

## Snabbstart
### Konfigurera Miljövariabler
```
cd backend
copy .env.example .env
```

### Installera Backend-beroenden med uv

```
cd backend

# Synkronisera och installera alla beroenden (skapar virtuell miljö automatiskt)
uv sync

# Eller ange Python-version
uv sync --python 3.11
```

### Initiera Databas
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Starta Backend-tjänst
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Obs: `uv run` använder automatiskt Python från projektets virtuella miljö, ingen manuell aktivering krävs.

Backend körs på http://localhost:8000

API-dokumentation: http://localhost:8000/docs

### Installera Frontend-beroenden
```
cd frontend
npm install
```

### Starta Frontend-utveklingsserver

```
cd frontend
npm run dev
```
Frontend körs på http://localhost:5173

## Snabbstartsskript (Windows)

### Starta Backend med ett klick

Skapa `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Starta Frontend med ett klick

Skapa `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Starta alla tjänster med ett klick

Skapa `start_all.bat`:
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

## Docker-uträttning (Valfritt)

Om du använder Docker, se till att Docker Desktop är installerat, och kör sedan:

```bash
docker-compose up -d
```

Detta startar både frontend- och backend-tjänster.

**Obs:** Miljövariabler måste först konfigureras i `backend/.env`.


## Språk som stöds

BookBook stöder följande gränssnittsspråk:

| Språk | Kod | Språk | Kod |
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

Totalt **82** stödda språk.

## Portbeskrivning

| Tjänst | Port | Beskrivning |
|------|------|------|
| Frontend (Vite) | 5173 | React-utveklingsserver |
| Backend (FastAPI) | 8000 | API-tjänst |
| P2P-sändning (UDP) | 47832 | LAN-nodupptäckt |
| P2P-boksynk (TCP) | 47833 | Bokdataöverföring |

**Brandväggsinställningar:**
Om du använder P2P-funktioner, se till att portarna 47832 (UDP) och 47833 (TCP) är öppna på ditt LAN.
