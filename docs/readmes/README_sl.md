# BookBook - AI eBook Generator

> **AI generator eBookov, ki vam omogoča ustvarjanje čudovitih eBookov z pomočjo AI.**

## Hitri Začetek
### Konfiguracija Okoljskih Spremenljivk
```
cd backend
copy .env.example .env
```

### Namestitev Backend Odvisnosti z uv

```
cd backend

# Sinhronizacija in namestitev vseh odvisnosti (samodejno ustvari virtualno okolje)
uv sync

# Ali določite verzijo Python
uv sync --python 3.11
```

### Inicializacija Baze Podatkov
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Zagon Backend Storitve
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Opomba: `uv run` samodejno uporablja Python iz virtualnega okolja projekta, ročna aktivacija ni potrebna.

Backend bo deloval na http://localhost:8000

API dokumentacija: http://localhost:8000/docs

### Namestitev Frontend Odvisnosti
```
cd frontend
npm install
```

### Zagon Frontend Razvojnega Strenika

```
cd frontend
npm run dev
```
Frontend bo deloval na http://localhost:5173


---

---

## Docker Namestitev (Opcijsko)

Če uporabljate Docker, se prepričajte, da je Docker Desktop nameščen, nato zaženite:

```bash
docker-compose up -d
```

To bo zagonilo frontend in backend storitve.

**Opomba:** Okoljske spremenljivke je treba najprej konfigurirati v `backend/.env`.


## Podprti Jeziki

BookBook podpira naslednje jezike vmesnika:

| Jezik | Koda | Jezik | Koda |
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

Skupaj **82** podprtih jezikov.

## Opis Vrat

| Storitev | Vrata | Opis |
|------|------|------|
| Frontend (Vite) | 5173 | React razvojni strežnik |
| Backend (FastAPI) | 8000 | API storitev |
| P2P Broadcast (UDP) | 47832 | Odkrivanje LAN vozlišč |
| P2P Book Sync (TCP) | 47833 | Prenos podatkov knjig |

**Nastavitve Požarnega Zidu:**
Če uporabljate P2P funkcije, se prepričajte, da so vrata 47832 (UDP) in 47833 (TCP) odprta v vaši LAN.
