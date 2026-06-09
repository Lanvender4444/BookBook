# BookBook - Generatore di eBook con AI

## Inizio Rapido
### Configura le Variabili d'Ambiente
```
cd backend
copy .env.example .env
```

### Installa le Dipendenze del Backend con uv

```
cd backend

# Sincronizza e installa tutte le dipendenze (crea l'ambiente virtuale automaticamente)
uv sync

# O specifica la versione di Python
uv sync --python 3.11
```

### Inizializza il Database
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Avvia il Servizio Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Nota: `uv run` usa automaticamente Python dall'ambiente virtuale del progetto, non è necessaria l'attivazione manuale.

Il backend funzionerà su http://localhost:8000

Documentazione API: http://localhost:8000/docs

### Installa le Dipendenze del Frontend
```
cd frontend
npm install
```

### Avvia il Server di Sviluppo Frontend

```
cd frontend
npm run dev
```
Il frontend funzionerà su http://localhost:5173

## Script di Avvio Rapido (Windows)

### Avvia il Backend con Un Solo Clic

Crea `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Avvia il Frontend con Un Solo Clic

Crea `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Avvia Tutti i Servizi con Un Solo Clic

Crea `start_all.bat`:
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

## Deploy con Docker (Opzionale)

Se usi Docker, assicurati che Docker Desktop sia installato, poi esegui:

```bash
docker-compose up -d
```

Questo avvierà sia il frontend che il backend.

**Nota:** Le variabili d'ambiente devono prima essere configurate in `backend/.env`.


## Lingue Supportate

BookBook supporta le seguenti lingue dell'interfaccia:

| Lingua | Codice | Lingua | Codice |
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

Totale **82** lingue supportate.

## Descrizione delle Porte

| Servizio | Porta | Descrizione |
|------|------|------|
| Frontend (Vite) | 5173 | Server di sviluppo React |
| Backend (FastAPI) | 8000 | Servizio API |
| Broadcast P2P (UDP) | 47832 | Scoperta nodi LAN |
| Sincronizzazione P2P (TCP) | 47833 | Trasferimento dati libri |

**Impostazioni Firewall:**
Se usi le funzionalità P2P, assicurati che le porte 47832 (UDP) e 47833 (TCP) siano aperte nella tua LAN.
