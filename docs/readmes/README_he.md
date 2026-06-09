# BookBook - AI eBook מחולל

> **🌐 其他语言 / Other Languages / Otros Idiomas / 他の言語 / 다른 언어**
>
> [Afrikaans](README_af.md) | [العربية](README_ar.md) | [Azərbaycan](README_az.md) | [Български](README_bg.md) | [বাংলা](README_bn.md) | [Català](README_ca.md) | [Cebuano](README_ceb.md) | [Čeština](README_cs.md) | [Dansk](README_da.md) | [Deutsch](README_de.md) | [Ελληνικά](README_el.md) | [English](README_en.md) | [Español](README_es.md) | [Eesti](README_et.md) | [Euskara](README_eu.md) | [فارسی](README_fa.md) | [Suomi](README_fi.md) | [Filipino](README_fil.md) | [Français](README_fr.md) | [Galego](README_gl.md) | [עברית](README_he.md) | [हिन्दी](README_hi.md) | [Hrvatski](README_hr.md) | [Magyar](README_hu.md) | [Bahasa Indonesia](README_id.md) | [Íslenska](README_is.md) | [Italiano](README_it.md) | [日本語](README_ja.md) | [Jawa](README_jv.md) | [한국어](README_ko.md) | [Latina](README_la.md) | [Lietuvių](README_lt.md) | [Latviešu](README_lv.md) | [Macedonian](README_mk.md) | [Melayu](README_ms.md) | [Norsk bokmål](README_nb.md) | [Nederlands](README_nl.md) | [Norsk nynorsk](README_nn.md) | [Norsk](README_no.md) | [Polski](README_pl.md) | [Português (Brasil)](README_pt-BR.md) | [Português (Portugal)](README_pt-PT.md) | [Română](README_ro.md) | [Русский](README_ru.md) | [Slovenčina](README_sk.md) | [Slovenščina](README_sl.md) | [Shqip](README_sq.md) | [Srpski](README_sr.md) | [Svenska](README_sv.md) | [தமிழ்](README_ta.md) | [తెలుగు](README_te.md) | [ไทย](README_th.md) | [Türkçe](README_tr.md) | [Українська](README_uk.md) | [اردو](README_ur.md) | [Tiếng Việt](README_vi.md) | [繁體中文](README_zh-TW.md) | [中文（简体）](../README.md)

---


> **An AI-powered eBook generator that lets you create beautiful ebooks with AI assistance.**

## התחלה מהירה
### הגדרת משתני סביבה
```
cd backend
copy .env.example .env
```

### התקנת תלויות Backend עם uv

```
cd backend

# סנכרון והתקנת כל התלויות (יוצר סביבה וירטואלית אוטומטית)
uv sync

# או ציין גרסת Python
uv sync --python 3.11
```

### אתחול מסד נתונים
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### הפעלת שירות Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
הערה: `uv run` משתמש אוטומטית ב-Python מהסביבה הווירטואלית של הפרויקט, אין צורך בפעולה ידנית.

Backend יפעל ב-http://localhost:8000

תיעוד API: http://localhost:8000/docs

### התקנת תלויות Frontend
```
cd frontend
npm install
```

### הפעלת שרת פיתוח Frontend

```
cd frontend
npm run dev
```
Frontend יפעל ב-http://localhost:5173

## סקריפטים להתחלה מהירה (Windows)

### הפעלת Backend בלחיצה אחת

צור `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### הפעלת Frontend בלחיצה אחת

צור `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### הפעלת כל השירותים בלחיצה אחת

צור `start_all.bat`:
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

## פריסת Docker (אופציונלי)

אם אתה משתמש ב-Docker, ודא ש-Docker Desktop מותקן, ואז הפעל:

```bash
docker-compose up -d
```

זה יפעיל את שירותי Frontend ו-Backend.

**הערה:** משתני סביבה חייבים להיות מוגדרים תחילה ב-`backend/.env`.


## שפות נתמכות

BookBook תומך בשפות הממשק הבאות:

| שפה | קוד | שפה | קוד |
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

סך הכל **82** שפות נתמכות.

## תיאור פורטים

| שירות | פורט | תיאור |
|------|------|------|
| Frontend (Vite) | 5173 | שרת פיתוח React |
| Backend (FastAPI) | 8000 | שירות API |
| שידור P2P (UDP) | 47832 | גילוי צמתים ברשת המקומית |
| סנכרון ספרים P2P (TCP) | 47833 | העברת נתוני ספרים |

**הגדרות חומת אש:**
אם אתה משתמש בתכונות P2P, ודא שפורטים 47832 (UDP) ו-47833 (TCP) פתוחים ברשת המקומית שלך.
