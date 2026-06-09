# BookBook - AI eBook Generator

## Snelle Start
### Omgevingsvariabelen Configureren
```
cd backend
copy .env.example .env
```

### Backend Afhankelijkheden Installeren met uv

```
cd backend

# Alle afhankelijkheden synchroniseren en installeren (maakt virtuele omgeving automatisch aan)
uv sync

# Of Python versie specificeren
uv sync --python 3.11
```

### Database Initialiseren
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend Service Starten
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Opmerking: `uv run` gebruikt automatisch Python uit de virtuele omgeving van het project, geen handmatige activering nodig.

Backend draait op http://localhost:8000

API documentatie: http://localhost:8000/docs

### Frontend Afhankelijkheden Installeren
```
cd frontend
npm install
```

### Frontend Development Server Starten

```
cd frontend
npm run dev
```
Frontend draait op http://localhost:5173

## Snelle Start Scripts (Windows)

### Backend Starten met Één Klik

Maak `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Frontend Starten met Één Klik

Maak `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Alle Services Starten met Één Klik

Maak `start_all.bat`:
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

## Docker Implementatie (Optioneel)

Als u Docker gebruikt, zorg ervoor dat Docker Desktop is geïnstalleerd, en voer dan uit:

```bash
docker-compose up -d
```

Dit start zowel de frontend als backend services.

**Opmerking:** Omgevingsvariabelen moeten eerst worden geconfigureerd in `backend/.env`.


## Ondersteunde Talen

BookBook ondersteunt de volgende interface-talen:

| Taal | Code | Taal | Code |
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

Totaal **82** ondersteunde talen.

## Port Beschrijving

| Service | Port | Beschrijving |
|------|------|------|
| Frontend (Vite) | 5173 | React development server |
| Backend (FastAPI) | 8000 | API service |
| P2P Broadcast (UDP) | 47832 | LAN node discovery |
| P2P Book Sync (TCP) | 47833 | Boek data overdracht |

**Firewall Instellingen:**
Als u P2P functionaliteit gebruikt, zorg ervoor dat poorten 47832 (UDP) en 47833 (TCP) open zijn op uw LAN.
