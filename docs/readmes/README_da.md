# BookBook - AI eBook Generator

## Hurtig Start
### Konfigurer Miljøvariable
```
cd backend
copy .env.example .env
```

### Installer Backend-afhængigheder med uv

```
cd backend

# Synkroniser og installer alle afhængigheder (opretter virtuelt miljø automatisk)
uv sync

# Eller specificer Python-version
uv sync --python 3.11
```

### Initialiser Database
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Start Backend-tjeneste
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Bemærk: `uv run` bruger automatisk Python fra projektets virtuelle miljø, ingen manuel aktivering nødvendig.

Backend kører på http://localhost:8000

API-dokumentation: http://localhost:8000/docs

### Installer Frontend-afhængigheder
```
cd frontend
npm install
```

### Start Frontend-udviklingsserver

```
cd frontend
npm run dev
```
Frontend kører på http://localhost:5173

## Hurtigstartsskripter (Windows)

### Start Backend med ét klik

Opret `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Start Frontend med ét klik

Opret `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Start alle tjenester med ét klik

Opret `start_all.bat`:
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

## Docker-udrulning (Valgfri)

Hvis du bruger Docker, skal du sørge for at Docker Desktop er installeret, og derefter køre:

```bash
docker-compose up -d
```

Dette starter både frontend- og backend-tjenester.

**Bemærk:** Miljøvariable skal først konfigureres i `backend/.env`.


## Understøttede Sprog

BookBook understøtter følgende interfacesprog:

| Sprog | Kode | Sprog | Kode |
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

I alt **82** understøttede sprog.

## Portbeskrivelse

| Tjeneste | Port | Beskrivelse |
|------|------|------|
| Frontend (Vite) | 5173 | React-udviklingsserver |
| Backend (FastAPI) | 8000 | API-tjeneste |
| P2P-roadcast (UDP) | 47832 | LAN-nodeopdagelse |
| P2P-bogsynk (TCP) | 47833 | Bogdataoverførsel |

**Firewall-indstillinger:**
Hvis du bruger P2P-funktioner, skal du sørge for at portene 47832 (UDP) og 47833 (TCP) er åbne på dit LAN.
