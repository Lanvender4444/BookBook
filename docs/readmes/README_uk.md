# BookBook - ІІ Генератор Електронних Книг

> **🌐 其他语言 / Other Languages / Otros Idiomas / 他の言語 / 다른 언어**
>
> [Afrikaans](README_af.md) | [العربية](README_ar.md) | [Azərbaycan](README_az.md) | [Български](README_bg.md) | [বাংলা](README_bn.md) | [Català](README_ca.md) | [Cebuano](README_ceb.md) | [Čeština](README_cs.md) | [Dansk](README_da.md) | [Deutsch](README_de.md) | [Ελληνικά](README_el.md) | [English](README_en.md) | [Español](README_es.md) | [Eesti](README_et.md) | [Euskara](README_eu.md) | [فارسی](README_fa.md) | [Suomi](README_fi.md) | [Filipino](README_fil.md) | [Français](README_fr.md) | [Galego](README_gl.md) | [עברית](README_he.md) | [हिन्दी](README_hi.md) | [Hrvatski](README_hr.md) | [Magyar](README_hu.md) | [Bahasa Indonesia](README_id.md) | [Íslenska](README_is.md) | [Italiano](README_it.md) | [日本語](README_ja.md) | [Jawa](README_jv.md) | [한국어](README_ko.md) | [Latina](README_la.md) | [Lietuvių](README_lt.md) | [Latviešu](README_lv.md) | [Macedonian](README_mk.md) | [Melayu](README_ms.md) | [Norsk bokmål](README_nb.md) | [Nederlands](README_nl.md) | [Norsk nynorsk](README_nn.md) | [Norsk](README_no.md) | [Polski](README_pl.md) | [Português (Brasil)](README_pt-BR.md) | [Português (Portugal)](README_pt-PT.md) | [Română](README_ro.md) | [Русский](README_ru.md) | [Slovenčina](README_sk.md) | [Slovenščina](README_sl.md) | [Shqip](README_sq.md) | [Srpski](README_sr.md) | [Svenska](README_sv.md) | [தமிழ்](README_ta.md) | [తెలుగు](README_te.md) | [ไทย](README_th.md) | [Türkçe](README_tr.md) | [Українська](README_uk.md) | [اردو](README_ur.md) | [Tiếng Việt](README_vi.md) | [繁體中文](README_zh-TW.md) | [简体中文](../../README.md)

---


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
