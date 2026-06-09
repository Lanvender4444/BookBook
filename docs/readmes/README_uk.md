# BookBook - ІІ Генератор Електронних Книг

> **ІІ-генератор електронних книг, який дозволяє створювати красиві ebooks за допомогою ІІ.**

## Швидкий Старт
### Налаштування Змінних Середовища
```
cd backend
copy .env.example .env
```

### Встановлення Залежностей Бекенда за допомогою uv

```
cd backend

# Синхронізація та встановлення всіх залежностей (автоматично створює віртуальне середовище)
uv sync

# Або вказати версію Python
uv sync --python 3.11
```

### Ініціалізація Бази Даних
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Запуск Сервісу Бекенда
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Примітка: `uv run` автоматично використовує Python з віртуального середовища проекту, активація не потрібна.

Бекенд працюватиме за адресою http://localhost:8000

Документація API: http://localhost:8000/docs

### Встановлення Залежностей Фронтенда
```
cd frontend
npm install
```

### Запуск Сервера Розробки Фронтенда

```
cd frontend
npm run dev
```
Фронтенд працюватиме за адресою http://localhost:5173


---

---

## Розгортання через Docker (Опціонально)

Якщо ви використовуєте Docker, переконайтеся що Docker Desktop встановлений, потім виконайте:

```bash
docker-compose up -d
```

Це запустить як фронтенд, так і бекенд сервіси.

**Примітка:** Спочатку необхідно налаштувати змінні середовища в `backend/.env`.


## Підтримувані Мови

BookBook підтримує наступні мови інтерфейсу:

| Мова | Код | Мова | Код |
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

Всього **82** підтримуваних мови.

## Опис Портів

| Сервіс | Порт | Опис |
|------|------|------|
| Фронтенд (Vite) | 5173 | Сервер розробки React |
| Бекенд (FastAPI) | 8000 | API сервіс |
| P2P-roadcast (UDP) | 47832 | Виявлення вузлів LAN |
| P2P-Синхронізація (TCP) | 47833 | Передача даних книг |

**Налаштування фаерволу:**
Якщо ви використовуєте P2P функції, переконайтеся що порти 47832 (UDP) і 47833 (TCP) відкриті у вашій LAN.
