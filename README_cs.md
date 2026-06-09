# BookBook - AI eBook Generátor

## Rychlý Start
### Nastavení Proměnných Prostředí
```
cd backend
copy .env.example .env
```

### Instalace Závislostí Backendu pomocí uv

```
cd backend

# Synchronizace a instalace všech závislostí (automaticky vytvoří virtuální prostředí)
uv sync

# Nebo určit verzi Python
uv sync --python 3.11
```

### Inicializace Databáze
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Spuštění Služby Backendu
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Poznámka: `uv run` automaticky používá Python z virtuálního prostředí projektu, není potřeba ruční aktivace.

Backend bude běžet na http://localhost:8000

Dokumentace API: http://localhost:8000/docs

### Instalace Závislostí Frontendu
```
cd frontend
npm install
```

### Spuštění Vývojového Serveru Frontendu

```
cd frontend
npm run dev
```
Frontend bude běžet na http://localhost:5173

## Skripty Rychlého Spuštění (Windows)

### Spuštění Backendu jedním kliknutím

Vytvořit `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Spuštění Frontendu jedním kliknutím

Vytvořit `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Spuštění Všech Služeb jedním kliknutím

Vytvořit `start_all.bat`:
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

## Nasazení Docker (Volitelné)

Pokud používáte Docker, ujistěte se, že je Docker Desktop nainstalován, poté spusťte:

```bash
docker-compose up -d
```

Toto spustí frontend i backend služby.

**Poznámka:** Proměnné prostředí musí být nejprve nakonfigurovány v `backend/.env`.


## Podporované Jazyky

BookBook podporuje následující jazyky rozhraní:

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

Celkem **82** podporovaných jazyků.

## Popis Portů

| Služba | Port | Popis |
|------|------|------|
| Frontend (Vite) | 5173 | Vývojový server React |
| Backend (FastAPI) | 8000 | API služba |
| P2P Broadcast (UDP) | 47832 | Objevování uzlů LAN |
| P2P Book Sync (TCP) | 47833 | Přenos dat knih |

**Nastavení Firewallu:**
Pokud používáte P2P funkce, ujistěte se, že porty 47832 (UDP) a 47833 (TCP) jsou otevřené ve vaší LAN.
