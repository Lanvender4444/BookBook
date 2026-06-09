# BookBook - AI eBook Generator

> **AI eBook generator, mis võimaldab luua kauneid e-raamatuid AI toega.**

## Kiire Alustamine
### Keskkonnamuutujate Seadistamine
```
cd backend
copy .env.example .env
```

### Backend Sõltuvuste Installimine uv-ga

```
cd backend

# Sünkroniseerimine ja kõigi sõltuvuste installimine (loob virtuaalkeskkonna automaatselt)
uv sync

# Või määrake Python-i versioon
uv sync --python 3.11
```

### Andmebaasi Initsialiseerimine
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend Teenuse Käivitamine
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Märkus: `uv run` kasutab automaatselt projekti virtuaalkeskkonna Python-i, käsitsi aktiveerimine pole vajalik.

Backend töötab aadressil http://localhost:8000

API dokumentatsioon: http://localhost:8000/docs

### Frontend Sõltuvuste Installimine
```
cd frontend
npm install
```

### Frontend Arendusserveri Käivitamine

```
cd frontend
npm run dev
```
Frontend töötab aadressil http://localhost:5173


---

---

## Docker Paigaldamine (Valikuline)

Kui kasutate Dockerit, veenduge, et Docker Desktop on installitud, seejärel käivitage:

```bash
docker-compose up -d
```

See käivitab nii frontend kui ka backend teenused.

**Märkus:** Keskkonnamuutujad tuleb esmalt seadistada `backend/.env` failis.


## Toetatud Keeled

BookBook toetab järgmisi kasutajaliidese keeli:

| Keel | Kood | Keel | Kood |
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

Kokku **82** toetatud keelt.

## Portide Kirjeldus

| Teenus | Port | Kirjeldus |
|------|------|------|
| Frontend (Vite) | 5173 | React arendusserver |
| Backend (FastAPI) | 8000 | API teenus |
| P2P Edastus (UDP) | 47832 | LAN sõlmede tuvastamine |
| P2P Raamatute Sünkroonimine (TCP) | 47833 | Raamatuandmete edastamine |

**Tulemüüri Seaded:**
Kui kasutate P2P funktsioone, veenduge, et portid 47832 (UDP) ja 47833 (TCP) on avatud teie võrgus.
