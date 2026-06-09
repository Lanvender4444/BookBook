# BookBook - Xerador de Libros Electrónicos con IA

> **🌐 其他语言 / Other Languages / Otros Idiomas / 他の言語 / 다른 언어**
>
> [Afrikaans](README_af.md) | [العربية](README_ar.md) | [Azərbaycan](README_az.md) | [Български](README_bg.md) | [বাংলা](README_bn.md) | [Català](README_ca.md) | [Cebuano](README_ceb.md) | [Čeština](README_cs.md) | [Dansk](README_da.md) | [Deutsch](README_de.md) | [Ελληνικά](README_el.md) | [English](README_en.md) | [Español](README_es.md) | [Eesti](README_et.md) | [Euskara](README_eu.md) | [فارسی](README_fa.md) | [Suomi](README_fi.md) | [Filipino](README_fil.md) | [Français](README_fr.md) | [Galego](README_gl.md) | [עברית](README_he.md) | [हिन्दी](README_hi.md) | [Hrvatski](README_hr.md) | [Magyar](README_hu.md) | [Bahasa Indonesia](README_id.md) | [Íslenska](README_is.md) | [Italiano](README_it.md) | [日本語](README_ja.md) | [Jawa](README_jv.md) | [한국어](README_ko.md) | [Latina](README_la.md) | [Lietuvių](README_lt.md) | [Latviešu](README_lv.md) | [Macedonian](README_mk.md) | [Melayu](README_ms.md) | [Norsk bokmål](README_nb.md) | [Nederlands](README_nl.md) | [Norsk nynorsk](README_nn.md) | [Norsk](README_no.md) | [Polski](README_pl.md) | [Português (Brasil)](README_pt-BR.md) | [Português (Portugal)](README_pt-PT.md) | [Română](README_ro.md) | [Русский](README_ru.md) | [Slovenčina](README_sk.md) | [Slovenščina](README_sl.md) | [Shqip](README_sq.md) | [Srpski](README_sr.md) | [Svenska](README_sv.md) | [தமிழ்](README_ta.md) | [తెలుగు](README_te.md) | [ไทย](README_th.md) | [Türkçe](README_tr.md) | [Українська](README_uk.md) | [اردو](README_ur.md) | [Tiếng Việt](README_vi.md) | [繁體中文](README_zh-TW.md)

---


> **Un xerador de libros electrónicos con IA que che permite crear ebooks bonitos con asistencia de IA.**

## Inicio Rápido
### Configurar Variábeis de Contorno
```
cd backend
copy .env.example .env
```

### Instalar Dependencias do Backend con uv

```
cd backend

# Sincronizar e instalar todas as dependencias (crea o contorno virtual automaticamente)
uv sync

# Ou especificar a versión de Python
uv sync --python 3.11
```

### Inicializar a Base de Datos
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Iniciar o Servizo Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Nota: `uv run` usa automaticamente Python do contorno virtual do proxecto, non é necesaria a activación manual.

O backend executarase en http://localhost:8000

Documentación da API: http://localhost:8000/docs

### Instalar Dependencias do Frontend
```
cd frontend
npm install
```

### Iniciar o Servidor de Desenvolvemento Frontend

```
cd frontend
npm run dev
```
O frontend executarase en http://localhost:5173


---

---

## Despregue con Docker (Opcional)

Se usa Docker, asegúrese de que Docker Desktop está instalado, logo execute:

```bash
docker-compose up -d
```

Isto iniciará tanto o frontend como o backend.

**Nota:** As variábeis de contorno deben configurarse primeiro en `backend/.env`.


## Idiomas Soportados

BookBook soporta os seguintes idiomas de interface:

| Idioma | Código | Idioma | Código |
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

Total de **82** idiomas soportados.

## Descrición dos Portos

| Servizo | Porto | Descrición |
|------|------|------|
| Frontend (Vite) | 5173 | Servidor de desenvolvemento React |
| Backend (FastAPI) | 8000 | Servizo API |
| Difusión P2P (UDP) | 47832 | Descuberta de nodos LAN |
| Sincronización P2P (TCP) | 47833 | Transferencia de datos de libros |

**Configuración de Cortafuegos:**
Se usa funcionalidades P2P, asegúrese de que os portos 47832 (UDP) e 47833 (TCP) están abertos na súa LAN.
