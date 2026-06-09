# BookBook - AI eBook Ģenerators

## Ātra Sākšana
### Vides Mainīgo Konfigurēšana
```
cd backend
copy .env.example .env
```

### Backend Atkarību Instalēšana ar uv

```
cd backend

# Sinhronizēt un instalēt visas atkarības (automātiski izveido virtuālo vidi)
uv sync

# Vai norādiet Python versiju
uv sync --python 3.11
```

### Datubāzes Inicializācija
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend Pakalpojuma Palaišana
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Piezīme: `uv run` automātiski izmanto Python no projekta virtuālās vides, manuāla aktivēšana nav nepieciešama.

Backend darbosies adresē http://localhost:8000

API dokumentācija: http://localhost:8000/docs

### Frontend Atkarību Instalēšana
```
cd frontend
npm install
```

### Frontend Izstrādes Servera Palaišana

```
cd frontend
npm run dev
```
Frontend darbosies adresē http://localhost:5173

## Ātrās Palaišanas Skripti (Windows)

### Backend Palaišana ar Vienu Klikšķi

Izveidot `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Frontend Palaišana ar Vienu Klikšķi

Izveidot `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Visu Pakalpojumu Palaišana ar Vienu Klikšķi

Izveidot `start_all.bat`:
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

## Docker Ieviešana (Izvēles)

Ja izmantojat Docker, pārliecinieties, ka Docker Desktop ir instalēts, pēc tam palaidiet:

```bash
docker-compose up -d
```

Tas palaidīs gan frontend, gan backend pakalpojumus.

**Piezīme:** Vispirms jākonfigurē vides mainīgie `backend/.env` failā.


## Atbalstītās Valodas

BookBook atbalsta šādas saskarnes valodas:

| Valoda | Kods | Valoda | Kods |
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

Kopā **82** atbalstītas valodas.

## Portu Apraksts

| Pakalpojums | Ports | Apraksts |
|------|------|------|
| Frontend (Vite) | 5173 | React izstrādes serveris |
| Backend (FastAPI) | 8000 | API pakalpojums |
| P2P Pārraide (UDP) | 47832 | LAN mezglu atklāšana |
| P2P Grāmatu Sinhronizācija (TCP) | 47833 | Grāmatu datu pārsūtīšana |

**Firewall Iestatījumi:**
Ja izmantojat P2P funkcijas, pārliecinieties, ka porti 47832 (UDP) un 47833 (TCP) ir atvērti jūsu LAN tīklā.
