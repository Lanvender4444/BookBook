# BookBook - Generador de eBooks con IA

> **🌐 其他语言 / Other Languages / Otros Idiomas / 他の言語 / 다른 언어**
>
> [Afrikaans](README_af.md) | [العربية](README_ar.md) | [Azərbaycan](README_az.md) | [Български](README_bg.md) | [বাংলা](README_bn.md) | [Català](README_ca.md) | [Cebuano](README_ceb.md) | [Čeština](README_cs.md) | [Dansk](README_da.md) | [Deutsch](README_de.md) | [Ελληνικά](README_el.md) | [English](README_en.md) | [Español](README_es.md) | [Eesti](README_et.md) | [Euskara](README_eu.md) | [فارسی](README_fa.md) | [Suomi](README_fi.md) | [Filipino](README_fil.md) | [Français](README_fr.md) | [Galego](README_gl.md) | [עברית](README_he.md) | [हिन्दी](README_hi.md) | [Hrvatski](README_hr.md) | [Magyar](README_hu.md) | [Bahasa Indonesia](README_id.md) | [Íslenska](README_is.md) | [Italiano](README_it.md) | [日本語](README_ja.md) | [Jawa](README_jv.md) | [한국어](README_ko.md) | [Latina](README_la.md) | [Lietuvių](README_lt.md) | [Latviešu](README_lv.md) | [Macedonian](README_mk.md) | [Melayu](README_ms.md) | [Norsk bokmål](README_nb.md) | [Nederlands](README_nl.md) | [Norsk nynorsk](README_nn.md) | [Norsk](README_no.md) | [Polski](README_pl.md) | [Português (Brasil)](README_pt-BR.md) | [Português (Portugal)](README_pt-PT.md) | [Română](README_ro.md) | [Русский](README_ru.md) | [Slovenčina](README_sk.md) | [Slovenščina](README_sl.md) | [Shqip](README_sq.md) | [Srpski](README_sr.md) | [Svenska](README_sv.md) | [தமிழ்](README_ta.md) | [తెలుగు](README_te.md) | [ไทย](README_th.md) | [Türkçe](README_tr.md) | [Українська](README_uk.md) | [اردو](README_ur.md) | [Tiếng Việt](README_vi.md) | [繁體中文](README_zh-TW.md) | [简体中文](../../README.md)

---


> **Un generador de eBooks impulsado por IA que te permite crear hermosos ebooks con asistencia de IA.**

## Inicio Rápido
### Configurar Variables de Entorno
```
cd backend
copy .env.example .env
```

### Instalar Dependencias del Backend con uv

```
cd backend

# Sincronizar e instalar todas las dependencias (crea entorno virtual automáticamente)
uv sync

# O especificar versión de Python
uv sync --python 3.11
```

### Inicializar Base de Datos
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Iniciar Servicio Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Nota: `uv run` usa automáticamente Python del entorno virtual del proyecto, no es necesario activarlo manualmente.

El backend se ejecutará en http://localhost:8000

Documentación de la API: http://localhost:8000/docs

### Instalar Dependencias del Frontend
```
cd frontend
npm install
```

### Iniciar Servidor de Desarrollo del Frontend

```
cd frontend
npm run dev
```
El frontend se ejecutará en http://localhost:5173


---

---

## Despliegue con Docker (Opcional)

Si usa Docker, asegúrese de tener Docker Desktop instalado, luego ejecute:

```bash
docker-compose up -d
```

Esto iniciará tanto el frontend como el backend.

**Nota:** Primero debe configurar las variables de entorno en `backend/.env`.


## Idiomas Soportados

BookBook soporta los siguientes idiomas de interfaz:

| Idioma | Código | Idioma | Código |
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

Total de **82** idiomas soportados.

## Descripción de Puertos

| Servicio | Puerto | Descripción |
|------|------|------|
| Frontend (Vite) | 5173 | Servidor de desarrollo React |
| Backend (FastAPI) | 8000 | Servicio API |
| Difusión P2P (UDP) | 47832 | Descubrimiento de nodos LAN |
| Sincronización P2P (TCP) | 47833 | Transferencia de datos de libros |

**Configuración de Firewall:**
Si usa funcionalidades P2P, asegúrese de que los puertos 47832 (UDP) y 47833 (TCP) estén abiertos en su LAN.
