# BookBook - AI eBook Generatori

## Nopea Aloitus
### Ympäristömuuttujien Asetus
```
cd backend
copy .env.example .env
```

### Backend-riippuvuudet uv:lla

```
cd backend

# Synkronoi ja asenna kaikki riippuvuudet (luo virtuaaliympäristön automaattisesti)
uv sync

# Tai määritä Python-versio
uv sync --python 3.11
```

### Tietokannan Alustus
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend-palvelun Käynnistys
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Huomautus: `uv run` käyttää automaattisesti projektin virtuaaliympäristön Pythonia, manuaalinen aktivointi ei ole tarpeen.

Backend toimii osoitteessa http://localhost:8000

API-dokumentaatio: http://localhost:8000/docs

### Frontend-riippuvuudet
```
cd frontend
npm install
```

### Frontend-kehityspalvelimen Käynnistys

```
cd frontend
npm run dev
```
Frontend toimii osoitteessa http://localhost:5173

## Nopea-aloitusskriptit (Windows)

### Backend-näppäimistöyksinpainallus

Luo `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Frontend-näppäimistöyksinpainallus

Luo `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Kaikkien palvelujen käynnistys näppäimistöyksinpainalluksella

Luo `start_all.bat`:
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

## Docker-julkaisu (Valinnainen)

Jos käytät Dockeria, varmista että Docker Desktop on asennettu, ja suorita sitten:

```bash
docker-compose up -d
```

Tämä käynnistää sekä frontend- että backend-palvelut.

**Huomautus:** Ympäristömuuttujat on asetettava ensin `backend/.env`-tiedostoon.


## Tuetut Kielet

BookBook tukee seuraavia käyttöliittymäkieliä:

| Kieli | Koodi | Kieli | Koodi |
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

Yhteensä **82** tuettua kieltä.

## Porttien Kuvaus

| Palvelu | Portti | Kuvaus |
|------|------|------|
| Frontend (Vite) | 5173 | React-kehityspalvelin |
| Backend (FastAPI) | 8000 | API-palvelu |
| P2P-lähetys (UDP) | 47832 | LAN-solmun havaitseminen |
| P2P-kirjasynkronointi (TCP) | 47833 | Kirjatietojen siirto |

**Palomuuriasetukset:**
Jos käytät P2P-ominaisuuksia, varmista että portit 47832 (UDP) ja 47833 (TCP) ovat auki LAN-verkossasi.
