# BookBook - AI eBook ஜெனரேட்டர்

> **🌐 其他语言 / Other Languages / Otros Idiomas / 他の言語 / 다른 언어**
>
> [Afrikaans](README_af.md) | [العربية](README_ar.md) | [Azərbaycan](README_az.md) | [Български](README_bg.md) | [বাংলা](README_bn.md) | [Català](README_ca.md) | [Cebuano](README_ceb.md) | [Čeština](README_cs.md) | [Dansk](README_da.md) | [Deutsch](README_de.md) | [Ελληνικά](README_el.md) | [English](README_en.md) | [Español](README_es.md) | [Eesti](README_et.md) | [Euskara](README_eu.md) | [فارسی](README_fa.md) | [Suomi](README_fi.md) | [Filipino](README_fil.md) | [Français](README_fr.md) | [Galego](README_gl.md) | [עברית](README_he.md) | [हिन्दी](README_hi.md) | [Hrvatski](README_hr.md) | [Magyar](README_hu.md) | [Bahasa Indonesia](README_id.md) | [Íslenska](README_is.md) | [Italiano](README_it.md) | [日本語](README_ja.md) | [Jawa](README_jv.md) | [한국어](README_ko.md) | [Latina](README_la.md) | [Lietuvių](README_lt.md) | [Latviešu](README_lv.md) | [Macedonian](README_mk.md) | [Melayu](README_ms.md) | [Norsk bokmål](README_nb.md) | [Nederlands](README_nl.md) | [Norsk nynorsk](README_nn.md) | [Norsk](README_no.md) | [Polski](README_pl.md) | [Português (Brasil)](README_pt-BR.md) | [Português (Portugal)](README_pt-PT.md) | [Română](README_ro.md) | [Русский](README_ru.md) | [Slovenčina](README_sk.md) | [Slovenščina](README_sl.md) | [Shqip](README_sq.md) | [Srpski](README_sr.md) | [Svenska](README_sv.md) | [தமிழ்](README_ta.md) | [తెలుగు](README_te.md) | [ไทย](README_th.md) | [Türkçe](README_tr.md) | [Українська](README_uk.md) | [اردو](README_ur.md) | [Tiếng Việt](README_vi.md) | [繁體中文](README_zh-TW.md)

---


> **AI மூலம் அழகான eBooks உருவாக்க உதவும் AI eBook ஜெனரேட்டர்।**

## விரைவு தொடக்கம்
### சுற்றுப்பாடு மாறிகளை கட்டமைக்கவும்
```
cd backend
copy .env.example .env
```

### uv மூலம் Backend சார்புநிலைகளை நிறுவவும்

```
cd backend

# அனைத்து சார்புநிலைகளையும் ஒத்திசைத்து நிறுவவும் (மெய்நிகர் சூழலை தானாக உருவாக்குகிறது)
uv sync

# அல்லது Python பதிப்பைக் குறிப்பிடவும்
uv sync --python 3.11
```

### தரவுத்தளத்தை துவக்கவும்
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend சேவையைத் தொடங்கவும்
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
குறிப்பு: `uv run` தானாகவே திட்டத்தின் மெய்நிகர் சூழலின் Python ஐப் பயன்படுத்துகிறது, கைமுறையாக செயல்படுத்த வேண்டிய அவசியமில்லை.

Backend http://localhost:8000 இல் இயங்கும்

API ஆவணம்: http://localhost:8000/docs

### Frontend சார்புநிலைகளை நிறுவவும்
```
cd frontend
npm install
```

### Frontend உருவாக்க சேவையகத்தைத் தொடங்கவும்

```
cd frontend
npm run dev
```
Frontend http://localhost:5173 இல் இயங்கும்

## விரைவு தொடக்க ஸ்கிரிப்ட்கள் (Windows)

### ஒரே கிளிக்கில் Backend ஐத் தொடங்கவும்

`start_backend.bat` உருவாக்கவும்:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### ஒரே கிளிக்கில் Frontend ஐத் தொடங்கவும்

`start_frontend.bat` உருவாக்கவும்:
```batch
@echo off
cd frontend
npm run dev
pause
```

### ஒரே கிளிக்கில் அனைத்து சேவைகளையும் தொடங்கவும்

`start_all.bat` உருவாக்கவும்:
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

## Docker விநியோகம் (விருப்பத்தேர்வு)

Docker ஐப் பயன்படுத்தினால், Docker Desktop நிறுவப்பட்டுள்ளதா என்பதை உறுதிசெய்து, பின்னர் இயக்கவும்:

```bash
docker-compose up -d
```

இது frontend மற்றும் backend சேவைகள் இரண்டையும் தொடங்கும்.

**குறிப்பு:** முதலில் `backend/.env` இல் சுற்றுப்பாடு மாறிகளை கட்டமைக்க வேண்டும்.


## ஆதரிக்கப்படும் மொழிகள்

BookBook பின்வரும் இடைமுக மொழிகளை ஆதரிக்கிறது:

| மொழி | குறியீடு | மொழி | குறியீடு |
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

மொத்தம் **82** ஆதரிக்கப்படும் மொழிகள்.

## போர்ட் விளக்கம்

| சேவை | போர்ட் | விளக்கம் |
|------|------|------|
| Frontend (Vite) | 5173 | React உருவாக்க சேவையகம் |
| Backend (FastAPI) | 8000 | API சேவை |
| P2P ஒலிபரப்பு (UDP) | 47832 | LAN முனை கண்டறிதல் |
| P2P புத்தக ஒத்திசைவு (TCP) | 47833 | புத்தக தரவு பரிமாற்றம் |

**ஃபயர்வால் அமைப்புகள்:**
P2P அம்சங்களைப் பயன்படுத்தினால், போர்ட் 47832 (UDP) மற்றும் 47833 (TCP) உங்கள் LAN இல் திறந்திருப்பதை உறுதிசெய்யவும்.
