# BookBook - مولّد الكتب الإلكترونية بالذكاء الاصطناعي

## البدء السريع
### تهيئة متغيرات البيئة
```
cd backend
copy .env.example .env
```

### تثبيت تبعيات الخلفية باستخدام uv

```
cd backend

# مزامنة وتثبيت جميع التبعيات (يتم إنشاء البيئة الافتراضية تلقائياً)
uv sync

# أو تحديد إصدار Python
uv sync --python 3.11
```

### تهيئة قاعدة البيانات
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### تشغيل خدمة الخلفية
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
ملاحظة: `uv run` يستخدم تلقائياً Python من البيئة الافتراضية للمشروع، لا حاجة للتفعيل اليدوي.

ستعمل الخلفية على http://localhost:8000

توثيق API: http://localhost:8000/docs

### تثبيت تبعيات الواجهة الأمامية
```
cd frontend
npm install
```

### تشغيل خادم تطوير الواجهة الأمامية

```
cd frontend
npm run dev
```
ستعمل الواجهة الأمامية على http://localhost:5173

## نصوص التشغيل السريع (Windows)

### تشغيل الخلفية بنقرة واحدة

إنشاء `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### تشغيل الواجهة الأمامية بنقرة واحدة

إنشاء `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### تشغيل جميع الخدمات بنقرة واحدة

إنشاء `start_all.bat`:
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

## النشر باستخدام Docker (اختياري)

إذا كنت تستخدم Docker، تأكد من تثبيت Docker Desktop، ثم قم بتشغيل:

```bash
docker-compose up -d
```

سيتم تشغيل كل من الواجهة الأمامية والخلفية.

**ملاحظة:** يجب تهيئة متغيرات البيئة أولاً في `backend/.env`.


## اللغات المدعومة

يدعم BookBook اللغات التالية لواجهة المستخدم:

| اللغة | الرمز | اللغة | الرمز |
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

إجمالي **82** لغة مدعومة.

## وصف المنافذ

| الخدمة | المنفذ | الوصف |
|------|------|------|
| الواجهة الأمامية (Vite) | 5173 | خادم تطوير React |
| الخلفية (FastAPI) | 8000 | خدمة API |
| البث P2P (UDP) | 47832 | اكتشاف عقد الشبكة المحلية |
| مزامنة الكتب P2P (TCP) | 47833 | نقل بيانات الكتب |

**إعدادات جدار الحماية:**
إذا كنت تستخدم ميزات P2P، تأكد من أن المنافذ 47832 (UDP) و 47833 (TCP) مفتوحة في شبكتك المحلية.
