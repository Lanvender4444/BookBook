# BookBook - AI eBook Generator

> **🌐 其他语言 / Other Languages / Otros Idiomas / 他の言語 / 다른 언어**
>
> [Afrikaans](README_af.md) | [العربية](README_ar.md) | [Azərbaycan](README_az.md) | [Български](README_bg.md) | [বাংলা](README_bn.md) | [Català](README_ca.md) | [Cebuano](README_ceb.md) | [Čeština](README_cs.md) | [Dansk](README_da.md) | [Deutsch](README_de.md) | [Ελληνικά](README_el.md) | [English](README_en.md) | [Español](README_es.md) | [Eesti](README_et.md) | [Euskara](README_eu.md) | [فارسی](README_fa.md) | [Suomi](README_fi.md) | [Filipino](README_fil.md) | [Français](README_fr.md) | [Galego](README_gl.md) | [עברית](README_he.md) | [हिन्दी](README_hi.md) | [Hrvatski](README_hr.md) | [Magyar](README_hu.md) | [Bahasa Indonesia](README_id.md) | [Íslenska](README_is.md) | [Italiano](README_it.md) | [日本語](README_ja.md) | [Jawa](README_jv.md) | [한국어](README_ko.md) | [Latina](README_la.md) | [Lietuvių](README_lt.md) | [Latviešu](README_lv.md) | [Macedonian](README_mk.md) | [Melayu](README_ms.md) | [Norsk bokmål](README_nb.md) | [Nederlands](README_nl.md) | [Norsk nynorsk](README_nn.md) | [Norsk](README_no.md) | [Polski](README_pl.md) | [Português (Brasil)](README_pt-BR.md) | [Português (Portugal)](README_pt-PT.md) | [Română](README_ro.md) | [Русский](README_ru.md) | [Slovenčina](README_sk.md) | [Slovenščina](README_sl.md) | [Shqip](README_sq.md) | [Srpski](README_sr.md) | [Svenska](README_sv.md) | [தமிழ்](README_ta.md) | [తెలుగు](README_te.md) | [ไทย](README_th.md) | [Türkçe](README_tr.md) | [Українська](README_uk.md) | [اردو](README_ur.md) | [Tiếng Việt](README_vi.md) | [繁體中文](README_zh-TW.md) | [中文（简体）](../README.md)

---


> **AI-aangedrewe eBook-generator wat jou toelaat om mooi eBoeke te skep met AI-ondersteuning.**

## Vinnige Begin
### Omgewing Veranderlikes Konfigureer
```
cd backend
copy .env.example .env
```

### Backend Afhanklikhede Installeer met uv

```
cd backend

# Sien en installeer alle afhanklikhede (skep virtuele omgewing outomaties)
uv sync

# Of spesifiseer Python weergawe
uv sync --python 3.11
```

### Inisialiseer Databasis
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Begin Backend Diens
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Let wel: `uv run` gebruik outomaties Python uit die projek se virtuele omgewing, handmatige aktivering is nie nodig nie.

Backend sal by http://localhost:8000 loop

API dokumentasie: http://localhost:8000/docs

### Installeer Frontend Afhanklikhede
```
cd frontend
npm install
```

### Begin Frontend Ontwikkelings Bediener

```
cd frontend
npm run dev
```
Frontend sal by http://localhost:5173 loop


---

---

## Docker Implementasie (Opsioneel)

As jy Docker gebruik, maak seker Docker Desktop geïnstalleer is, en voer dan uit:

```bash
docker-compose up -d
```

Dit sal sowel frontend as backend dienste begin.

**Let wel:** Omgewing veranderlikes moet eers in `backend/.env` gekonfigureer word.


## Ondersteunde Tale

BookBook ondersteun die volgende koppelvlak tale:

| Taal | Kode | Taal | Kode |
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

Totaal **82** ondersteunde tale.

## Poort Beskrywing

| Diens | Poort | Beskrywing |
|------|------|------|
| Frontend (Vite) | 5173 | React ontwikkelings bediener |
| Backend (FastAPI) | 8000 | API diens |
| P2P Uitsending (UDP) | 47832 | LAN node ontdekking |
| P2P Boek Sinkronisasie (TCP) | 47833 | Boek data oordrag |

**Firewall Instellings:**
As jy P2P funksies gebruik, maak seker dat poorte 47832 (UDP) en 47833 (TCP) oop is op jou LAN.
