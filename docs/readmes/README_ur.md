# BookBook - AI eBook جنریٹر

> **🌐 其他语言 / Other Languages / Otros Idiomas / 他の言語 / 다른 언어**
>
> [Afrikaans](README_af.md) | [العربية](README_ar.md) | [Azərbaycan](README_az.md) | [Български](README_bg.md) | [বাংলা](README_bn.md) | [Català](README_ca.md) | [Cebuano](README_ceb.md) | [Čeština](README_cs.md) | [Dansk](README_da.md) | [Deutsch](README_de.md) | [Ελληνικά](README_el.md) | [English](README_en.md) | [Español](README_es.md) | [Eesti](README_et.md) | [Euskara](README_eu.md) | [فارسی](README_fa.md) | [Suomi](README_fi.md) | [Filipino](README_fil.md) | [Français](README_fr.md) | [Galego](README_gl.md) | [עברית](README_he.md) | [हिन्दी](README_hi.md) | [Hrvatski](README_hr.md) | [Magyar](README_hu.md) | [Bahasa Indonesia](README_id.md) | [Íslenska](README_is.md) | [Italiano](README_it.md) | [日本語](README_ja.md) | [Jawa](README_jv.md) | [한국어](README_ko.md) | [Latina](README_la.md) | [Lietuvių](README_lt.md) | [Latviešu](README_lv.md) | [Macedonian](README_mk.md) | [Melayu](README_ms.md) | [Norsk bokmål](README_nb.md) | [Nederlands](README_nl.md) | [Norsk nynorsk](README_nn.md) | [Norsk](README_no.md) | [Polski](README_pl.md) | [Português (Brasil)](README_pt-BR.md) | [Português (Portugal)](README_pt-PT.md) | [Română](README_ro.md) | [Русский](README_ru.md) | [Slovenčina](README_sk.md) | [Slovenščina](README_sl.md) | [Shqip](README_sq.md) | [Srpski](README_sr.md) | [Svenska](README_sv.md) | [தமிழ்](README_ta.md) | [తెలుగు](README_te.md) | [ไทย](README_th.md) | [Türkçe](README_tr.md) | [Українська](README_uk.md) | [اردو](README_ur.md) | [Tiếng Việt](README_vi.md) | [繁體中文](README_zh-TW.md) | [简体中文](../../README.md)

---


> **AI چالیت eBook جنریٹر جو آپ کو AI مدد سے خوبصورت eBooks بنانے کی اجازت دیتا ہے۔**

## تیز شروع
### ماحول کی تبدیلی کو ترتیب دیں
```
cd backend
copy .env.example .env
```

### uv کے ساتھ بیک اینڈ انڈیپینڈنسیز انسٹال کریں

```
cd backend

# تمام انڈیپینڈنسیز کو سنک اور انسٹال کریں (خودکار طور پر ورچوئل ماحول بناتا ہے)
uv sync

# یا پائیتھون ورژن مقرر کریں
uv sync --python 3.11
```

### ڈیٹا بیس شروع کریں
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### بیک اینڈ سروس شروع کریں
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
نوٹ: `uv run` خودکار طور پر پروجیکٹ کے ورچوئل ماحول کا پائیتھون استعمال کرتا ہے، دستی فعال کرکے ضرورت نہیں ہے۔

بیک اینڈ http://localhost:8000 پر چلے گا

ای پی آئی دستاویز: http://localhost:8000/docs

### فرنٹ اینڈ انڈیپینڈنسیز انسٹال کریں
```
cd frontend
npm install
```

### فرنٹ اینڈ ڈویلپمنٹ سرور شروع کریں

```
cd frontend
npm run dev
```
فرنٹ اینڈ http://localhost:5173 پر چلے گا

## تیز شروع اسکرپٹس (وینڈوز)

### ایک کلک میں بیک اینڈ شروع کریں

`start_backend.bat` بنائیں:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### ایک کلک میں فرنٹ اینڈ شروع کریں

`start_frontend.bat` بنائیں:
```batch
@echo off
cd frontend
npm run dev
pause
```

### ایک کلک میں تمام سروسز شروع کریں

`start_all.bat` بنائیں:
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

## ڈوکر ڈیپلوائمنٹ (اختیاری)

اگر آپ ڈوکر استعمال کر رہے ہیں، تو یقینی بنائیں کہ ڈوکر ڈیسکٹاپ انسٹل ہے، پھر چلائیں:

```bash
docker-compose up -d
```

یہ فرنٹ اینڈ اور بیک اینڈ دونوں سروسز شروع کرے گا۔

**نوٹ:** پہلے `backend/.env` میں ماحول کی تبدیلیوں کو ترتیب دینا ہوگا۔


## تعاون یافتہ زبانیں

BookBook مندرجہ ذیل انٹرفیس زبانوں کی تعاون کرتا ہے:

| زبان | کوڈ | زبان | کوڈ |
|------|------|------|------|
| 简体中文 | zh-CN | 中文（繁體） | zh-TW |
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

کل **82** تعاون یافتہ زبانیں۔

## پورٹ کی وضاحت

| سروس | پورٹ | وضاحت |
|------|------|------|
| فرنٹ اینڈ (Vite) | 5173 | ری ایکٹ ڈویلپمنٹ سرور |
| بیک اینڈ (FastAPI) | 8000 | ای پی آئی سروس |
| P2P براؤڈکاسٹ (UDP) | 47832 | LAN نوڈ دریافت |
| P2P کتاب مطابقت (TCP) | 47833 | کتاب ڈیٹا ٹرانسفر |

**فائر وال کی ترتیبات:**
اگر آپ P2P خصوصیات استعمال کر رہے ہیں، تو یقینی بنائیں کہ پورٹ 47832 (UDP) اور 47833 (TCP) آپ کے LAN میں کھلے ہیں۔
