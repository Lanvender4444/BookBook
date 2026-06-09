# BookBook - AI eBook Generator

> **An AI-powered eBook generator that lets you create beautiful ebooks with AI assistance.**

## Rask Start
### Konfigurer Miljøvariabler
```
cd backend
copy .env.example .env
```

### Installer Backend-avhengigheter med uv

```
cd backend

# Synkroniser og installer alle avhengigheter (oppretter virtuelt miljø automatisk)
uv sync

# Eller spesifiser Python-versjon
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
Merk: `uv run` bruker automatisk Python fra prosjektets virtuelle miljø, ingen manuell aktivering nødvendig.

Backend kjører på http://localhost:8000

API-dokumentasjon: http://localhost:8000/docs

### Installer Frontend-avhengigheter
```
cd frontend
npm install
```

### Start Frontend-utviklingsserver

```
cd frontend
npm run dev
```
Frontend kjører på http://localhost:5173


---

---

## Docker-utplassering (Valgfri)

Hvis du bruker Docker, sørg for at Docker Desktop er installert, og kjør deretter:

```bash
docker-compose up -d
```

Dette starter både frontend- og backend-tjenester.

**Merk:** Miljøvariabler må først konfigureres i `backend/.env`.


## Støttede Språk

BookBook støtter følgende grensesnittspråk:

| Språk | Kode | Språk | Kode |
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

Totalt **82** støttede språk.

## Portbeskrivelse

| Tjeneste | Port | Beskrivelse |
|------|------|------|
| Frontend (Vite) | 5173 | React-utviklingsserver |
| Backend (FastAPI) | 8000 | API-tjeneste |
| P2P-sending (UDP) | 47832 | LAN-nodoppdagelse |
| P2P-boksynk (TCP) | 47833 | Bokdataoverføring |

**Brannmurinnstillinger:**
Hvis du bruker P2P-funksjoner, sørg for at portene 47832 (UDP) og 47833 (TCP) er åpne på ditt LAN.
