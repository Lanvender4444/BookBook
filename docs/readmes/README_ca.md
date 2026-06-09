# BookBook - Generador de Llibres Electrònics amb IA

## Inici Ràpid
### Configurar Variables d'Entorn
```
cd backend
copy .env.example .env
```

### Instal·lar Dependències del Backend amb uv

```
cd backend

# Sincronitzar i instal·lar totes les dependències (crea entorn virtual automàticament)
uv sync

# O especificar versió de Python
uv sync --python 3.11
```

### Inicialitzar Base de Dades
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Iniciar Servei Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Nota: `uv run` utilitza automàticament Python de l'entorn virtual del projecte, no cal activació manual.

El backend s'executarà a http://localhost:8000

Documentació API: http://localhost:8000/docs

### Instal·lar Dependències del Frontend
```
cd frontend
npm install
```

### Iniciar Servidor de Desenvolupament Frontend

```
cd frontend
npm run dev
```
El frontend s'executarà a http://localhost:5173

## Scripts d'Inici Ràpid (Windows)

### Iniciar Backend amb Un Sol Clic

Crear `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Iniciar Frontend amb Un Sol Clic

Crear `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Iniciar Tots els Serveis amb Un Sol Clic

Crear `start_all.bat`:
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

## Desplegament amb Docker (Opcional)

Si utilitzeu Docker, assegureu-vos que Docker Desktop està instal·lat, i executeu:

```bash
docker-compose up -d
```

Això iniciarà tant el frontend com el backend.

**Nota:** Les variables d'entorn s'han de configurar primer a `backend/.env`.


## Idiomes Suportats

BookBook suporta els següents idiomes d'interfície:

| Idioma | Codi | Idioma | Codi |
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

Total de **82** idiomes suportats.

## Descripció de Ports

| Servei | Port | Descripció |
|------|------|------|
| Frontend (Vite) | 5173 | Servidor de desenvolupament React |
| Backend (FastAPI) | 8000 | Servei API |
| Difusió P2P (UDP) | 47832 | Descoberta de nodes LAN |
| Sincronització P2P (TCP) | 47833 | Transferència de dades de llibres |

**Configuració de Tallafocs:**
Si utilitzeu funcionalitats P2P, assegureu-vos que els ports 47832 (UDP) i 47833 (TCP) estan oberts a la vostra LAN.
