# BookBook - ИИ Генератор Электронных Книг

> **ИИ-генератор электронных книг, который позволяет создавать красивые ebooks с помощью ИИ.**

## Быстрый Старт
### Настройка Переменных Окружения
```
cd backend
copy .env.example .env
```

### Установка Зависимостей Бэкенда с uv

```
cd backend

# Синхронизация и установка всех зависимостей (автоматически создает виртуальное окружение)
uv sync

# Или указать версию Python
uv sync --python 3.11
```

### Инициализация Базы Данных
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Запуск Сервиса Бэкенда
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Примечание: `uv run` автоматически использует Python из виртуального окружения проекта, активация не требуется.

Бэкенд будет работать по адресу http://localhost:8000

Документация API: http://localhost:8000/docs

### Установка Зависимостей Фронтенда
```
cd frontend
npm install
```

### Запуск Сервера Разработки Фронтенда

```
cd frontend
npm run dev
```
Фронтенд будет работать по адресу http://localhost:5173


---

---

## Развёртывание через Docker (Опционально)

Если вы используете Docker, убедитесь что Docker Desktop установлен, затем выполните:

```bash
docker-compose up -d
```

Это запустит как фронтенд, так и бэкенд сервисы.

**Примечание:** Сначала необходимо настроить переменные окружения в `backend/.env`.


## Поддерживаемые Языки

BookBook поддерживает следующие языки интерфейса:

| Язык | Код | Язык | Код |
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

Всего **82** поддерживаемых языка.

## Описание Портов

| Сервис | Порт | Описание |
|------|------|------|
| Фронтенд (Vite) | 5173 | Сервер разработки React |
| Бэкенд (FastAPI) | 8000 | API сервис |
| P2P-ROADCAST (UDP) | 47832 | Обнаружение узлов LAN |
| P2P-Синхронизация (TCP) | 47833 | Передача данных книг |

**Настройка файрвола:**
Если вы используете P2P функции, убедитесь что порты 47832 (UDP) и 47833 (TCP) открыты в вашей LAN.
