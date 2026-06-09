# BookBook - AI eBook Generator

> **AI-powered eBook generator na nagbibigay-daan sa iyo na lumikha ng magagandang ebooks sa tulong ng AI.**

## Mabilis na Pagsisimula
### I-configure ang mga Environment Variable
```
cd backend
copy .env.example .env
```

### I-install ang mga Backend Dependency gamit ang uv

```
cd backend

# I-synchronize at i-install ang lahat ng dependency (awtomatikong gumagawa ng virtual environment)
uv sync

# O tukuyin ang bersyon ng Python
uv sync --python 3.11
```

### I-initialize ang Database
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Simulan ang Backend Service
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Tandaan: Ang `uv run` ay awtomatikong gumagamit ng Python mula sa virtual environment ng proyekto, hindi na kailangan ng manual na pag-activate.

Ang backend ay tatakbo sa http://localhost:8000

API documentation: http://localhost:8000/docs

### I-install ang mga Frontend Dependency
```
cd frontend
npm install
```

### Simulan ang Frontend Development Server

```
cd frontend
npm run dev
```
Ang frontend ay tatakbo sa http://localhost:5173


---

---

## Docker Deployment (Opsyonal)

Kung gumagamit ng Docker, siguraduhin na naka-install ang Docker Desktop, pagkatapos ay patakbuhin:

```bash
docker-compose up -d
```

Ito ay magpapatakbo ng frontend at backend na serbisyo.

**Tandaan:** Ang mga environment variable ay kailangang i-configure muna sa `backend/.env`.


## Mga Sinusuportahang Wika

Sumusuporta ang BookBook sa mga sumusunod na wika ng interface:

| Wika | Kode | Wika | Kode |
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

Kabuuang **82** sinusuportahang wika.

## Paglalarawan ng Port

| Serbisyo | Port | Paglalarawan |
|------|------|------|
| Frontend (Vite) | 5173 | React development server |
| Backend (FastAPI) | 8000 | API serbisyo |
| P2P Broadcast (UDP) | 47832 | LAN node discovery |
| P2P Book Sync (TCP) | 47833 | Paglilipat ng datos ng libro |

**Mga Setting ng Firewall:**
Kung gumagamit ng P2P features, siguraduhin na ang mga port 47832 (UDP) at 47833 (TCP) ay bukas sa iyong LAN.
