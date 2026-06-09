# BookBook - AI eBook Generator

> **AI-powered eBook generator nga magahatag kanimo og paghimo og maanyag nga eBooks uban sa tabang sa AI.**

## Pagsugod nga Dali
### Pag-configure sa Mga Environment Variable
```
cd backend
copy .env.example .env
```

### Pag-install sa Backend Dependencies gamit ang uv

```
cd backend

# I-synchronize ug i-install ang tanan nga dependencies (awtomatik nga mag-create sa virtual environment)
uv sync

# O specify ang Python version
uv sync --python 3.11
```

### Pag-initialize sa Database
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Pagsugod sa Backend Service
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Nota: Ang `uv run` awtomatik nga mogamit sa Python gikan sa virtual environment sa proyekto, dili kinahanglan ang manual nga pag-activate.

Ang backend molunggo sa http://localhost:8000

API documentation: http://localhost:8000/docs

### Pag-install sa Frontend Dependencies
```
cd frontend
npm install
```

### Pagsugod sa Frontend Development Server

```
cd frontend
npm run dev
```
Ang frontend molunggo sa http://localhost:5173


---

---

## Docker Deployment (Optional)

Kung gigamit ang Docker, siguradoa nga ang Docker Desktop na-install na, dayon i-run:

```bash
docker-compose up -d
```

Kini mogugma ang frontend ug backend nga services.

**Nota:** Ang environment variables kinahanglan una nga i-configure sa `backend/.env`.


## Mga Sinuportahan nga Lengguwahe

Ang BookBook nagsuporta sa mga mosunod nga interface nga lengguwahe:

| Lengguwahe | Kodigo | Lengguwahe | Kodigo |
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

Kabuohan **82** nga suportado nga lengguwahe.

## Paghulagway sa Port

| Serbisyo | Port | Paghulagway |
|------|------|------|
| Frontend (Vite) | 5173 | React development server |
| Backend (FastAPI) | 8000 | API serbisyo |
| P2P Broadcast (UDP) | 47832 | Pagdiskobre sa LAN node |
| P2P Book Sync (TCP) | 47833 | Pagbalhin sa datos sa libro |

**Mga Setting sa Firewall:**
Kung gigamit ang P2P features, siguradoa nga ang mga port 47832 (UDP) ug 47833 (TCP) abli sa imong LAN.
