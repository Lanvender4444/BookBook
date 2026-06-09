# BookBook - AI eBook Rúntrektari

> **AI knúinn eBook rúntrektari sem gerir þér kleift að búa til fallega eBooks með AI stuðningi.**

## Fljót Byrjun
### Stilltu Umhverfisbreytur
```
cd backend
copy .env.example .env
```

### Settu upp Backend Háðindi með uv

```

# Samstilltu og settu upp öll háðindi (býr til sýndarumhverfi sjálfkrafa)
uv sync

# Eða tilgreindu Python útgáfu
uv sync --python 3.11
```

### Frumstilltu Gagnagrunn
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Ræktu Backend Þjónustu
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Athugið: `uv run` notar sjálfkrafa Python úr sýndarumhverfi verkefnisins, engin handvirk virkjun þörf.

Backend mun keyra á http://localhost:8000

API skjölun: http://localhost:8000/docs

### Settu upp Frontend Háðindi
```
cd frontend
npm install
```

### Ræktu Frontend Þróunarþjónn

```
cd frontend
npm run dev
```
Frontend mun keyra á http://localhost:5173


---

---

## Docker Útsetning (Valfrjálst)

Ef þú notar Docker, gakktu úr skugga um að Docker Desktop sé uppsett, keyrðu síðan:

```bash
docker-compose up -d
```

Þetta mun ræsa bæði frontend og backend þjónustur.

**Athugið:** Umhverfisbreytur verða fyrst að stilla í `backend/.env`.


## Studd tungumál

BookBook styður eftirfarandi viðmóttungumál:

| Tungumál | Kóði | Tungumál | Kóði |
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

Samtals **82** studd tungumál.

## Lýsing Gáttar

| Þjónusta | Gátt | Lýsing |
|------|------|------|
| Frontend (Vite) | 5173 | React þróunarþjónn |
| Backend (FastAPI) | 8000 | API þjónusta |
| P2P Útvarp (UDP) | 47832 | LAN hnút uppgötvun |
| P2P Bóka Samstillt (TCP) | 47833 | Bóka gagnflutningur |

**Eldvegg stillingar:**
Ef þú notar P2P eiginleika, gakktu úr skugga um að gáttirnar 47832 (UDP) og 47833 (TCP) séu opnar í þínu LAN.
