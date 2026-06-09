# BookBook - AI eBook Generátor

> **AI-alapú eBook generátor, amely lehetővé teszi szép eBook-ok létrehozását AI segítséggel.**

## Gyors Kezdés
### Környezeti Változók Beállítása
```
cd backend
copy .env.example .env
```

### Backend Függőségek Telepítése uv-val

```
cd backend

# Összes függőség szinkronizálása és telepítése (automatikusan létrehozza a virtuális környezetet)
uv sync

# Vagy Python verzió megadása
uv sync --python 3.11
```

### Adatbázis Inicializálása
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend Szolgáltatás Indítása
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Megjegyzés: Az `uv run` automatikusan használja a projekt virtuális környezetének Python-ját, kézi aktiválás nem szükséges.

A backend a http://localhost:8000 címen fog futni

API dokumentáció: http://localhost:8000/docs

### Frontend Függőségek Telepítése
```
cd frontend
npm install
```

### Frontend Fejlesztői Szerver Indítása

```
cd frontend
npm run dev
```
A frontend a http://localhost:5173 címen fog futni

## Gyorsindító Szkriptek (Windows)

### Backend Indítása Egy Kattintással

Hozd létre a `start_backend.bat` fájlt:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Frontend Indítása Egy Kattintással

Hozd létre a `start_frontend.bat` fájlt:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Összes Szolgáltatás Indítása Egy Kattintással

Hozd létre a `start_all.bat` fájlt:
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

## Docker Telepítés (Opcionális)

Ha Docker-t használsz, győződj meg arról, hogy a Docker Desktop telepítve van, majd futtasd:

```bash
docker-compose up -d
```

Ez elindítja a frontend és backend szolgáltatásokat is.

**Megjegyzés:** A környezeti változókat előbb be kell állítani a `backend/.env` fájlban.


## Támogatott Nyelvek

A BookBook a felület következő nyelveit támogatja:

| Nyelv | Kód | Nyelv | Kód |
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

Összesen **82** támogatott nyelv.

## Port Leírás

| Szolgáltatás | Port | Leírás |
|------|------|------|
| Frontend (Vite) | 5173 | React fejlesztői szerver |
| Backend (FastAPI) | 8000 | API szolgáltatás |
| P2P Broadcast (UDP) | 47832 | LAN csomópont felfedezés |
| P2P Book Sync (TCP) | 47833 | Könyv adatátvitel |

**Tűzfal Beállítások:**
Ha P2P funkciókat használsz, győződj meg arról, hogy a 47832 (UDP) és 47833 (TCP) portok nyitva vannak a hálózatodon.
