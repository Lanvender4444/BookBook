# BookBook - AI eBook Sortzailea

## Hasiera Azkarrak
### Inguruko Aldagaiak Konfiguratu
```
cd backend
copy .env.example .env
```

### Backend Mendekotasunak Instalatu uv-rekin

```
cd backend

# Sinkronizatu eta instalatu mendekotasun guztiak (ingurune birtuala automatikoki sortzen du)
uv sync

# Edo zehaztu Python bertsioa
uv sync --python 3.11
```

### Datu-basea Hasieratu
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend Zerbitzuari Hasi
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Oharra: `uv run` automatikoki erabiltzen du proiektuaren ingurune birtualaren Python, ez da aktibazio eskuzkoa behar.

Backend http://localhost:8000 helbidean ibiliko da

API dokumentazioa: http://localhost:8000/docs

### Frontend Mendekotasunak Instalatu
```
cd frontend
npm install
```

### Frontend Garapen Zerbitzaria Hasi

```
cd frontend
npm run dev
```
Frontend http://localhost:5173 helbidean ibiliko da

## Hasiera Azkarraren Script-ak (Windows)

### Backend Klik Batekin Hasi

`start_backend.bat` sortu:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Frontend Klik Batekin Hasi

`start_frontend.bat` sortu:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Zerbitzu Guztiak Klik Batekin Hasi

`start_all.bat` sortu:
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

## Docker Despliegua (Aukerakoa)

Docker erabiltzen baduzu, ziurtatu Docker Desktop instalatuta dagoela, ondoren exekutatu:

```bash
docker-compose up -d
```

Honek frontend eta backend zerbitzuak abiaraziko ditu.

**Oharra:** Inguruko aldagaiak lehenik konfiguratu behar dira `backend/.env` fitxategian.


## Onartutako Hizkuntzak

BookBook interfazearen hizkuntza hauek onartzen ditu:

| Hizkuntza | Kodea | Hizkuntza | Kodea |
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

Guztira **82** onartutako hizkuntza.

## Port Deskribapena

| Zerbitzua | Port | Deskribapena |
|------|------|------|
| Frontend (Vite) | 5173 | React garapen zerbitzaria |
| Backend (FastAPI) | 8000 | API zerbitzua |
| P2P Broadcast (UDP) | 47832 | LAN nodo aurkikuntza |
| P2P Liburu Sinkronizazioa (TCP) | 47833 | Liburu datu transferentzia |

**Su-horma Ezarpenak:**
P2P eginberritik bazabiltza, ziurtatu 47832 (UDP) eta 47833 (TCP) portak zure LANean irekita daudela.
