# BookBook - AI eBook Generátor

## Rýchly Štart
### Nastavenie Premenných Prostredia
```
cd backend
copy .env.example .env
```

### Inštalácia Závislostí Backendu pomocou uv

```
cd backend

# Synchronizácia a inštalácia všetkých závislostí (automaticky vytvorí virtuálne prostredie)
uv sync

# Alebo určte verziu Python
uv sync --python 3.11
```

### Inicializácia Databázy
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Spustenie Služby Backendu
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Poznámka: `uv run` automaticky používa Python z virtuálneho prostredia projektu, nie je potrebná ručná aktivácia.

Backend bude bežať na http://localhost:8000

Dokumentácia API: http://localhost:8000/docs

### Inštalácia Závislostí Frontendu
```
cd frontend
npm install
```

### Spustenie Vývojového Servera Frontendu

```
cd frontend
npm run dev
```
Frontend bude bežať na http://localhost:5173

## Skripty Rýchleho Spustenia (Windows)

### Spustenie Backendu jedným kliknutím

Vytvoriť `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Spustenie Frontendu jedným kliknutím

Vytvoriť `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Spustenie Všetkých Služieb jedným kliknutím

Vytvoriť `start_all.bat`:
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

## Docker Nasadenie (Voliteľné)

Ak používate Docker, uistite sa, že je Docker Desktop nainštalovaný, potom spustite:

```bash
docker-compose up -d
```

Toto spustí frontend aj backend služby.

**Poznámka:** Premenné prostredia musia byť najprv nakonfigurované v `backend/.env`.


## Podporované Jazyky

BookBook podporuje nasledujúce jazyky rozhrania:

| Jazyk | Kód | Jazyk | Kód |
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

Celkom **82** podporovaných jazykov.

## Popis Portov

| Služba | Port | Popis |
|------|------|------|
| Frontend (Vite) | 5173 | Vývojový server React |
| Backend (FastAPI) | 8000 | API služba |
| P2P Broadcast (UDP) | 47832 | Objevovanie uzlov LAN |
| P2P Book Sync (TCP) | 47833 | Prenos dát kníh |

**Nastavenia Firewallu:**
Ak používate P2P funkcie, uistite sa, že porty 47832 (UDP) a 47833 (TCP) sú otvorené vo vašej LAN.
