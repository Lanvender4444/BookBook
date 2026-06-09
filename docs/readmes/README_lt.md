# BookBook - AI eBook Generatorius

> **AI eBook generatorius, leidžiantis kurti gražias eBooks su AI pagalba.**

## Greitas Pradžia
### Aplinkos Kintamųjų Konfigūravimas
```
cd backend
copy .env.example .env
```

### Backend Priklausomybių Įdiegimas su uv

```
cd backend

# Sinchronizuoti ir įdiegti visas priklausomybes (automatiškai sukuria virtualią aplinką)
uv sync

# Arba nurodyti Python versiją
uv sync --python 3.11
```

### Duomenų Bazės Inicializavimas
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend Paslaugos Paleidimas
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Pastaba: `uv run` automatiškai naudoja Python iš projekto virtualios aplinkos, rankinis aktyvavimas nereikalingas.

Backend veiks adresu http://localhost:8000

API dokumentacija: http://localhost:8000/docs

### Frontend Priklausomybių Įdiegimas
```
cd frontend
npm install
```

### Frontend Kūrimo Serverio Paleidimas

```
cd frontend
npm run dev
```
Frontend veiks adresu http://localhost:5173

## Greito Paleidimo Scenarijai (Windows)

### Backend Paleidimas vienu Paspaudimu

Sukurti `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Frontend Paleidimas vienu Paspaudimu

Sukurti `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Visų Paslaugų Paleidimas vienu Paspaudimu

Sukurti `start_all.bat`:
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

## Docker Diegimas (Pasirinktinas)

Jei naudojate Docker, įsitikinkite, kad Docker Desktop įdiegtas, tada paleiskite:

```bash
docker-compose up -d
```

Tai paleis tiek frontend, tiek backend paslaugas.

**Pastaba:** Aplinkos kintamieji turi būti pirmiausia sukonfigūruoti `backend/.env` faile.


## Palaikomos Kalbos

BookBook palaiko šias sąsajos kalbas:

| Kalba | Kodas | Kalba | Kodas |
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

Iš viso **82** palaikomos kalbos.

## Portų Aprašymas

| Paslauga | Portas | Aprašymas |
|------|------|------|
| Frontend (Vite) | 5173 | React kūrimo serveris |
| Backend (FastAPI) | 8000 | API paslauga |
| P2P Transliavimas (UDP) | 47832 | LAN mazgų aptikimas |
| P2P Knygų Sinchronizavimas (TCP) | 47833 | Knygų duomenų perdavimas |

**Ugniasienės Nustatymai:**
Jei naudojate P2P funkcijas, įsitikinkite, kad portai 47832 (UDP) ir 47833 (TCP) yra atidaryti jūsų LAN tinkle.
