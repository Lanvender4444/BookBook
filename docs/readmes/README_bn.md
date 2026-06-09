# BookBook - AI eBook জেনারেটর

> **🌐 其他语言 / Other Languages / Otros Idiomas / 他の言語 / 다른 언어**
>
> [Afrikaans](README_af.md) | [العربية](README_ar.md) | [Azərbaycan](README_az.md) | [Български](README_bg.md) | [বাংলা](README_bn.md) | [Català](README_ca.md) | [Cebuano](README_ceb.md) | [Čeština](README_cs.md) | [Dansk](README_da.md) | [Deutsch](README_de.md) | [Ελληνικά](README_el.md) | [English](README_en.md) | [Español](README_es.md) | [Eesti](README_et.md) | [Euskara](README_eu.md) | [فارسی](README_fa.md) | [Suomi](README_fi.md) | [Filipino](README_fil.md) | [Français](README_fr.md) | [Galego](README_gl.md) | [עברית](README_he.md) | [हिन्दी](README_hi.md) | [Hrvatski](README_hr.md) | [Magyar](README_hu.md) | [Bahasa Indonesia](README_id.md) | [Íslenska](README_is.md) | [Italiano](README_it.md) | [日本語](README_ja.md) | [Jawa](README_jv.md) | [한국어](README_ko.md) | [Latina](README_la.md) | [Lietuvių](README_lt.md) | [Latviešu](README_lv.md) | [Macedonian](README_mk.md) | [Melayu](README_ms.md) | [Norsk bokmål](README_nb.md) | [Nederlands](README_nl.md) | [Norsk nynorsk](README_nn.md) | [Norsk](README_no.md) | [Polski](README_pl.md) | [Português (Brasil)](README_pt-BR.md) | [Português (Portugal)](README_pt-PT.md) | [Română](README_ro.md) | [Русский](README_ru.md) | [Slovenčina](README_sk.md) | [Slovenščina](README_sl.md) | [Shqip](README_sq.md) | [Srpski](README_sr.md) | [Svenska](README_sv.md) | [தமிழ்](README_ta.md) | [తెలుగు](README_te.md) | [ไทย](README_th.md) | [Türkçe](README_tr.md) | [Українська](README_uk.md) | [اردو](README_ur.md) | [Tiếng Việt](README_vi.md) | [繁體中文](README_zh-TW.md)

---


> **AI চালিত eBook জেনারেটর যা আপনাকে AI সহায়তায় সুন্দর eBooks তৈরি করতে দেয়।**

## দ্রুত শুরু
### পরিবেশ ভেরিয়েবল কনফিগার করুন
```
cd backend
copy .env.example .env
```

### uv দিয়ে Backend নির্ভরতা ইনস্টল করুন

```
cd backend

# সমস্ত নির্ভরতা সিঙ্ক এবং ইনস্টল করুন (স্বয়ংক্রিয়ভাবে ভার্চুয়াল এনভায়রনমেন্ট তৈরি করে)
uv sync

# অথবা Python সংস্করণ নির্দিষ্ট করুন
uv sync --python 3.11
```

### ডাটাবেস ইনিশিয়ালাইজ করুন
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend সেবা শুরু করুন
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
নোট: `uv run` স্বয়ংক্রিয়ভাবে প্রজেক্টের ভার্চুয়াল এনভায়রমেন্ট থেকে Python ব্যবহার করে, ম্যানুয়াল সক্রিয়করণ প্রয়োজন নেই।

Backend http://localhost:8000 এ চলবে

API ডকুমেন্টেশন: http://localhost:8000/docs

### Frontend নির্ভরতা ইনস্টল করুন
```
cd frontend
npm install
```

### Frontend ডেভেলপমেন্ট সার্ভার শুরু করুন

```
cd frontend
npm run dev
```
Frontend http://localhost:5173 এ চলবে

## দ্রুত শুরু স্ক্রিপ্ট (Windows)

### এক ক্লিকে Backend শুরু করুন

`start_backend.bat` তৈরি করুন:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### এক ক্লিকে Frontend শুরু করুন

`start_frontend.bat` তৈরি করুন:
```batch
@echo off
cd frontend
npm run dev
pause
```

### এক ক্লিকে সমস্ত সেবা শুরু করুন

`start_all.bat` তৈরি করুন:
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

## Docker ডিপ্লয়মেন্ট (ঐচ্ছিক)

Docker ব্যবহার করলে, Docker Desktop ইনস্টল করা আছে কিনা নিশ্চিত করুন, তারপর চালান:

```bash
docker-compose up -d
```

এটি ফ্রন্টএন্ড এবং ব্যাকএন্ড উভয় সেবা শুরু করবে।

**নোট:** প্রথমে `backend/.env` এ পরিবেশ ভেরিয়েবল কনফিগার করতে হবে।


## সমর্থিত ভাষা

BookBook নিম্নলিখিত ইন্টারফেস ভাষা সমর্থন করে:

| ভাষা | কোড | ভাষা | কোড |
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

মোট **82**টি সমর্থিত ভাষা।

## পোর্ট বিবরণ

| সেবা | পোর্ট | বিবরণ |
|------|------|------|
| Frontend (Vite) | 5173 | React ডেভেলপমেন্ট সার্ভার |
| Backend (FastAPI) | 8000 | API সেবা |
| P2P ব্রডকাস্ট (UDP) | 47832 | LAN নোড আবিষ্কার |
| P2P বই সিঙ্ক (TCP) | 47833 | বই ডেটা ট্রান্সফার |

**ফায়ারওয়াল সেটিংস:**
P2P বৈশিষ্ট্য ব্যবহার করলে, নিশ্চিত করুন পোর্ট 47832 (UDP) এবং 47833 (TCP) আপনার LAN এ খোলা আছে।
