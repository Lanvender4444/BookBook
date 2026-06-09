# BookBook - AI eBook Генератор

## Брз Старт
### Конфигурација на Променливи на Опкружувањето
```
cd backend
copy .env.example .env
```

### Инсталирање на Backend Зависности со uv

```
cd backend

# Синхронизација и инсталација на сите зависности (автоматски креира виртуелна средина)
uv sync

# Или специфицирајте Python верзија
uv sync --python 3.11
```

### Иницијализација на База на Податоци
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Стартување на Backend Сервисот
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Забелешка: `uv run` автоматски го користи Python од виртуелната средина на проектот, не е потребна рачна активација.

Backend ќе работи на http://localhost:8000

API документација: http://localhost:8000/docs

### Инсталирање на Frontend Зависности
```
cd frontend
npm install
```

### Стартување на Frontend Development Серверот

```
cd frontend
npm run dev
```
Frontend ќе работи на http://localhost:5173

## Брзи Старт Скрипти (Windows)

### Стартување на Backend со Еден Клик

Креирајте `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Стартување на Frontend со Еден Клик

Креирајте `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Стартување на Сите Сервиси со Еден Клик

Креирајте `start_all.bat`:
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

## Docker Деплој (Опционално)

Ако користите Docker, осигурајте се дека Docker Desktop е инсталиран, потоа извршете:

```bash
docker-compose up -d
```

Ова ќе ги стартира и frontend и backend сервисите.

**Забелешка:** Променливите на опкружувањето мора прво да се конфигурираат во `backend/.env`.


## Поддржани Јазици

BookBook ги поддржува следните јазици на интерфејсот:

| Јазик | Код | Јазик | Код |
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

Вкупно **82** поддржани јазици.

## Опис на Портови

| Сервис | Порт | Опис |
|------|------|------|
| Frontend (Vite) | 5173 | React development сервер |
| Backend (FastAPI) | 8000 | API сервис |
| P2P Broadcast (UDP) | 47832 | LAN откривање јазли |
| P2P Book Sync (TCP) | 47833 | Пренос на податоци за книги |

**Поставки на Firewall:**
Ако користите P2P функции, осигурајте се дека портите 47832 (UDP) и 47833 (TCP) се отворени во вашата LAN.
