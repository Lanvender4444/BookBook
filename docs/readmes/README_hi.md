# BookBook - AI eBook जनरेटर

> **🌐 其他语言 / Other Languages / Otros Idiomas / 他の言語 / 다른 언어**
>
> [Afrikaans](README_af.md) | [العربية](README_ar.md) | [Azərbaycan](README_az.md) | [Български](README_bg.md) | [বাংলা](README_bn.md) | [Català](README_ca.md) | [Cebuano](README_ceb.md) | [Čeština](README_cs.md) | [Dansk](README_da.md) | [Deutsch](README_de.md) | [Ελληνικά](README_el.md) | [English](README_en.md) | [Español](README_es.md) | [Eesti](README_et.md) | [Euskara](README_eu.md) | [فارسی](README_fa.md) | [Suomi](README_fi.md) | [Filipino](README_fil.md) | [Français](README_fr.md) | [Galego](README_gl.md) | [עברית](README_he.md) | [हिन्दी](README_hi.md) | [Hrvatski](README_hr.md) | [Magyar](README_hu.md) | [Bahasa Indonesia](README_id.md) | [Íslenska](README_is.md) | [Italiano](README_it.md) | [日本語](README_ja.md) | [Jawa](README_jv.md) | [한국어](README_ko.md) | [Latina](README_la.md) | [Lietuvių](README_lt.md) | [Latviešu](README_lv.md) | [Macedonian](README_mk.md) | [Melayu](README_ms.md) | [Norsk bokmål](README_nb.md) | [Nederlands](README_nl.md) | [Norsk nynorsk](README_nn.md) | [Norsk](README_no.md) | [Polski](README_pl.md) | [Português (Brasil)](README_pt-BR.md) | [Português (Portugal)](README_pt-PT.md) | [Română](README_ro.md) | [Русский](README_ru.md) | [Slovenčina](README_sk.md) | [Slovenščina](README_sl.md) | [Shqip](README_sq.md) | [Srpski](README_sr.md) | [Svenska](README_sv.md) | [தமிழ்](README_ta.md) | [తెలుగు](README_te.md) | [ไทย](README_th.md) | [Türkçe](README_tr.md) | [Українська](README_uk.md) | [اردو](README_ur.md) | [Tiếng Việt](README_vi.md) | [繁體中文](README_zh-TW.md) | [简体中文](../../README.md)

---


> **AI संचालित eBook जनरेटर जो आपको AI सहायता से सुंदर eBooks बनाने में मदद करता है।**

## त्वरित शुरुआत
### वातावरण चर कॉन्फ़िगर करें
```
cd backend
copy .env.example .env
```

### uv के साथ बैकएंड निर्भरताएँ स्थापित करें

```
cd backend

# सभी निर्भरताओं को सिंक करें और स्थापित करें (वर्चुअल एनवायरनमेंट स्वचालित रूप से बनाता है)
uv sync

# या Python संस्करण निर्दिष्ट करें
uv sync --python 3.11
```

### डेटाबेस इनिशियलाइज़ करें
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### बैकएंड सेवा शुरू करें
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
नोट: `uv run` स्वचालित रूप से प्रोजेक्ट के वर्चुअल एनवायरनमेंट का Python उपयोग करता है, मैनुअल सक्रियण की आवश्यकता नहीं है।

बैकएंड http://localhost:8000 पर चलेगा

API दस्तावेज़: http://localhost:8000/docs

### फ्रंटएंड निर्भरताएँ स्थापित करें
```
cd frontend
npm install
```

### फ्रंटएंड डेवलपमेंट सर्वर शुरू करें

```
cd frontend
npm run dev
```
फ्रंटएंड http://localhost:5173 पर चलेगा


---

---

## Docker तैनाती (वैकल्पिक)

यदि आप Docker का उपयोग करते हैं, तो सुनिश्चित करें कि Docker Desktop स्थापित है, फिर चलाएं:

```bash
docker-compose up -d
```

यह फ्रंटएंड और बैकएंड दोनों सेवाएँ शुरू करेगा।

**नोट:** पहले `backend/.env` में वातावरण चर कॉन्फ़िगर करने होंगे।


## समर्थित भाषाएँ

BookBook निम्नलिखित इंटरफ़ेस भाषाओं का समर्थन करता है:

| भाषा | कोड | भाषा | कोड |
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

कुल **82** समर्थित भाषाएँ।

## पोर्ट विवरण

| सेवा | पोर्ट | विवरण |
|------|------|------|
| फ्रंटएंड (Vite) | 5173 | React डेवलपमेंट सर्वर |
| बैकएंड (FastAPI) | 8000 | API सेवा |
| P2P ब्रॉडकास्ट (UDP) | 47832 | LAN नोड खोज |
| P2P पुस्तक सिंक (TCP) | 47833 | पुस्तक डेटा ट्रांसफर |

**फ़ायरवॉल सेटिंग्स:**
यदि आप P2P सुविधाओं का उपयोग करते हैं, तो सुनिश्चित करें कि पोर्ट 47832 (UDP) और 47833 (TCP) आपके LAN में खुले हैं।
