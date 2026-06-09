# BookBook - AI eBook Generator

## Vinnige Begin
### Omgewing Veranderlikes Konfigureer
```
cd backend
copy .env.example .env
```

### Backend Afhanklikhede Installeer met uv

```
cd backend

# Sien en installeer alle afhanklikhede (skep virtuele omgewing outomaties)
uv sync

# Of spesifiseer Python weergawe
uv sync --python 3.11
```

### Inisialiseer Databasis
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Begin Backend Diens
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Let wel: `uv run` gebruik outomaties Python uit die projek se virtuele omgewing, handmatige aktivering is nie nodig nie.

Backend sal by http://localhost:8000 loop

API dokumentasie: http://localhost:8000/docs

### Installeer Frontend Afhanklikhede
```
cd frontend
npm install
```

### Begin Frontend Ontwikkelings Bediener

```
cd frontend
npm run dev
```
Frontend sal by http://localhost:5173 loop

## Vinnige Begin Skripte (Windows)

### Begin Backend met Een Klik

Skep `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Begin Frontend met Een Klik

Skep `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Begin Alle Dienste met Een Klik

Skep `start_all.bat`:
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

## Docker Implementasie (Opsioneel)

As jy Docker gebruik, maak seker Docker Desktop geïnstalleer is, en voer dan uit:

```bash
docker-compose up -d
```

Dit sal sowel frontend as backend dienste begin.

**Let wel:** Omgewing veranderlikes moet eers in `backend/.env` gekonfigureer word.


## Ondersteunde Tale

BookBook ondersteun die volgende koppelvlak tale:

| Taal | Kode | Taal | Kode |
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

Totaal **82** ondersteunde tale.

## Poort Beskrywing

| Diens | Poort | Beskrywing |
|------|------|------|
| Frontend (Vite) | 5173 | React ontwikkelings bediener |
| Backend (FastAPI) | 8000 | API diens |
| P2P Uitsending (UDP) | 47832 | LAN node ontdekking |
| P2P Boek Sinkronisasie (TCP) | 47833 | Boek data oordrag |

**Firewall Instellings:**
As jy P2P funksies gebruik, maak seker dat poorte 47832 (UDP) en 47833 (TCP) oop is op jou LAN.
