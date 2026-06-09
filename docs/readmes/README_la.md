# BookBook - AI eBook Generator

> **AI liber eBook generator qui vos sinit creare pulchros eBooks cum AI auxilio.**

## Initium Celer
### Variabiles Ambientis Configurare
```
cd backend
copy .env.example .env
```

### Dependencias Backend Installare cum uv

```
cd backend

# Synchronizare et installare omnes dependencias (creat environment virtualem automatice)
uv sync

# Aut versionem Python specificare
uv sync --python 3.11
```

### Inicializare Database
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Servitium Backend Incipere
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Nota: `uv run` automatice utitur Python ex environment virtuale propositi, nulla activatio manualis necessaria est.

Backend currere apud http://localhost:8000

Documentatio API: http://localhost:8000/docs

### Dependencias Frontend Installare
```
cd frontend
npm install
```

### Servitium Frontend Development Incipere

```
cd frontend
npm run dev
```
Frontend currere apud http://localhost:5173


---

---

## Docker Dispositio (Electivum)

Si Docker uteris, fac ut Docker Desktop installatus sit, tum exequere:

```bash
docker-compose up -d
``>

Hoc Frontend et Backend servitia incipiet.

**Nota:** Variabiles ambientis primum in `backend/.env` configurandae sunt.


## Linguae Supportatae

BookBook has linguas interfacies supportat:

| Lingua | Codex | Lingua | Codex |
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

Total **82** linguae supportatae.

## Descriptio Portuum

| Servitium | Portus | Descriptio |
|------|------|------|
| Frontend (Vite) | 5173 | Servitor React development |
| Backend (FastAPI) | 8000 | Servitium API |
| P2P Broadcast (UDP) | 47832 | Invenitio nodorum LAN |
| P2P Book Sync (TCP) | 47833 | Translatio datorum librorum |

**Configurationes Ignis Parieti:**
Si P2P functiones uteris, fac ut portus 47832 (UDP) et 47833 (TCP) aperti sint in tuo LAN.
