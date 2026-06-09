# BookBook - AI eBook జెనరేటర్

> **🌐 其他语言 / Other Languages / Otros Idiomas / 他の言語 / 다른 언어**
>
> [Afrikaans](README_af.md) | [العربية](README_ar.md) | [Azərbaycan](README_az.md) | [Български](README_bg.md) | [বাংলা](README_bn.md) | [Català](README_ca.md) | [Cebuano](README_ceb.md) | [Čeština](README_cs.md) | [Dansk](README_da.md) | [Deutsch](README_de.md) | [Ελληνικά](README_el.md) | [English](README_en.md) | [Español](README_es.md) | [Eesti](README_et.md) | [Euskara](README_eu.md) | [فارسی](README_fa.md) | [Suomi](README_fi.md) | [Filipino](README_fil.md) | [Français](README_fr.md) | [Galego](README_gl.md) | [עברית](README_he.md) | [हिन्दी](README_hi.md) | [Hrvatski](README_hr.md) | [Magyar](README_hu.md) | [Bahasa Indonesia](README_id.md) | [Íslenska](README_is.md) | [Italiano](README_it.md) | [日本語](README_ja.md) | [Jawa](README_jv.md) | [한국어](README_ko.md) | [Latina](README_la.md) | [Lietuvių](README_lt.md) | [Latviešu](README_lv.md) | [Macedonian](README_mk.md) | [Melayu](README_ms.md) | [Norsk bokmål](README_nb.md) | [Nederlands](README_nl.md) | [Norsk nynorsk](README_nn.md) | [Norsk](README_no.md) | [Polski](README_pl.md) | [Português (Brasil)](README_pt-BR.md) | [Português (Portugal)](README_pt-PT.md) | [Română](README_ro.md) | [Русский](README_ru.md) | [Slovenčina](README_sk.md) | [Slovenščina](README_sl.md) | [Shqip](README_sq.md) | [Srpski](README_sr.md) | [Svenska](README_sv.md) | [தமிழ்](README_ta.md) | [తెలుగు](README_te.md) | [ไทย](README_th.md) | [Türkçe](README_tr.md) | [Українська](README_uk.md) | [اردو](README_ur.md) | [Tiếng Việt](README_vi.md) | [繁體中文](README_zh-TW.md)

---


> **AI సహాయంతో అందమైన eBooks సృష్టించడానికి మిమ్మల్ని అనుమతించే AI eBook జెనరేటర్।**

## త్వరిత ప్రారంభం
### ఎన్విరాన్మెంట్ వేరియబుల్స్ కాన్ఫిగర్ చేయండి
```
cd backend
copy .env.example .env
```

### uv తో Backend డిపెండెన్సీలు ఇన్‌స్టాల్ చేయండి

```
cd backend

# అన్ని డిపెండెన్సీలను సింక్ మరియు ఇన్‌స్టాల్ చేయండి (వర్చువల్ ఎన్విరాన్మెంట్‌ను స్వయంచాలకంగా సృష్టిస్తుంది)
uv sync

# లేదా Python వెర్షన్ నిర్దిష్టం చేయండి
uv sync --python 3.11
```

### డేటాబేస్ ఇనిషియలైజ్ చేయండి
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend సేవను ప్రారంభించండి
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
గమనిక: `uv run` స్వయంచాలకంగా ప్రాజెక్ట్ యొక్క వర్చువల్ ఎన్విరాన్మెంట్ Python ను ఉపయోగిస్తుంది, మాన్యువల్ యాక్టివేషన్ అవసరం లేదు.

Backend http://localhost:8000 లో నడుస్తుంది

API డాక్యుమెంటేషన్: http://localhost:8000/docs

### Frontend డిపెండెన్సీలు ఇన్‌స్టాల్ చేయండి
```
cd frontend
npm install
```

### Frontend డెవలప్‌మెంట్ సర్వర్ ప్రారంభించండి

```
cd frontend
npm run dev
```
Frontend http://localhost:5173 లో నడుస్తుంది

## త్వరిత ప్రారంభ స్క్రిప్ట్‌లు (Windows)

### ఒకే క్లిక్‌తో Backend ప్రారంభించండి

`start_backend.bat` సృష్టించండి:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### ఒకే క్లిక్‌తో Frontend ప్రారంభించండి

`start_frontend.bat` సృష్టించండి:
```batch
@echo off
cd frontend
npm run dev
pause
```

### ఒకే క్లిక్‌తో అన్ని సేవలు ప్రారంభించండి

`start_all.bat` సృష్టించండి:
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

## Docker డిప్లాయ్‌మెంట్ (ఐచ్ఛికం)

Docker ఉపయోగిస్తుంటే, Docker Desktop ఇన్‌స్టాల్ చేయబడిందని నిర్ధారించండి, ఆపై నడుపు:

```bash
docker-compose up -d
```

ఇది frontend మరియు backend సేవలను రెండింటినీ ప్రారంభిస్తుంది.

**గమనిక:** మొదట `backend/.env` లో ఎన్విరాన్మెంట్ వేరియబుల్స్ కాన్ఫిగర్ చేయాలి.


## మద్దతు ఉన్న భాషలు

BookBook కింది ఇంటర్‌ఫేస్ భాషలను మద్దతు ఇస్తుంది:

| భాష | కోడ్ | భాష | కోడ్ |
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

మొత్తం **82** మద్దతు ఉన్న భాషలు.

## పోర్ట్ వివరణ

| సేవ | పోర్ట్ | వివరణ |
|------|------|------|
| Frontend (Vite) | 5173 | React డెవలప్‌మెంట్ సర్వర్ |
| Backend (FastAPI) | 8000 | API సేవ |
| P2P ప్రసారం (UDP) | 47832 | LAN నోడ్ ఆవిష్కరణ |
| P2P పుస్తక సింక్ (TCP) | 47833 | పుస్తక డేటా బదిలీ |

**ఫైర్‌వాల్ సెట్టింగ్‌లు:**
P2P ఫీచర్లను ఉపయోగిస్తుంటే, పోర్ట్ 47832 (UDP) మరియు 47833 (TCP) మీ LAN లో తెరిచి ఉన్నాయని నిర్ధారించండి.
