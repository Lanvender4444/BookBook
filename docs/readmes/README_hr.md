# BookBook - AI eBook Generator

## Brzi Početak
### Konfiguracija Varijable Okruženja
```
cd backend
copy .env.example .env
```

### Instalacija Backend Zavisnosti sa uv

```
cd backend

# Sinkronizacija i instalacija svih zavisnosti (automatski kreira virtualno okruženje)
uv sync

# Ili specificirajte verziju Python
uv sync --python 3.11
```

### Inicijalizacija Baze Podataka
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Pokretanje Backend Servisa
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Napomena: `uv run` automatski koristi Python iz virtualnog okruženja projekta, ručna aktivacija nije potrebna.

Backend će raditi na http://localhost:8000

API dokumentacija: http://localhost:8000/docs

### Instalacija Frontend Zavisnosti
```
cd frontend
npm install
```

### Pokretanje Frontend Development Servera

```
cd frontend
npm run dev
```
Frontend će raditi na http://localhost:5173

## Skripte za Brzo Pokretanje (Windows)

### Pokretanje Backend sa Jednim Klikom

Kreirajte `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Pokretanje Frontend sa Jednim Klikom

Kreirajte `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Pokretanje Svihi Servisa sa Jednim Klikom

Kreirajte `start_all.bat`:
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

## Docker Deploy (Opcionalno)

Ako koristite Docker, pobrinite se da je Docker Desktop instaliran, zatim pokrenite:

```bash
docker-compose up -d
```

Ovo će pokrenuti i frontend i backend servise.

**Napomena:** Varijable okruženja moraju se prvo konfigurirati u `backend/.env`.


## Podržani Jezici

BookBook podržava sljedeće jezike sučelja:

| Jezik | Kod | Jezik | Kod |
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

Ukupno **82** podržanih jezika.

## Opis Portova

| Servis | Port | Opis |
|------|------|------|
| Frontend (Vite) | 5173 | React development server |
| Backend (FastAPI) | 8000 | API servis |
| P2P Broadcast (UDP) | 47832 | Otkrivanje LAN čvorova |
| P2P Book Sync (TCP) | 47833 | Prijenos podataka knjiga |

**Postavke Vatrozida:**
Ako koristite P2P funkcije, pobrinite se da su portovi 47832 (UDP) i 47833 (TCP) otvoreni u vašoj LAN mreži.
