# BookBook - AI電子書產生器

> **🌐 其他语言 / Other Languages / Otros Idiomas / 他の言語 / 다른 언어**
>
> [Afrikaans](README_af.md) | [العربية](README_ar.md) | [Azərbaycan](README_az.md) | [Български](README_bg.md) | [বাংলা](README_bn.md) | [Català](README_ca.md) | [Cebuano](README_ceb.md) | [Čeština](README_cs.md) | [Dansk](README_da.md) | [Deutsch](README_de.md) | [Ελληνικά](README_el.md) | [English](README_en.md) | [Español](README_es.md) | [Eesti](README_et.md) | [Euskara](README_eu.md) | [فارسی](README_fa.md) | [Suomi](README_fi.md) | [Filipino](README_fil.md) | [Français](README_fr.md) | [Galego](README_gl.md) | [עברית](README_he.md) | [हिन्दी](README_hi.md) | [Hrvatski](README_hr.md) | [Magyar](README_hu.md) | [Bahasa Indonesia](README_id.md) | [Íslenska](README_is.md) | [Italiano](README_it.md) | [日本語](README_ja.md) | [Jawa](README_jv.md) | [한국어](README_ko.md) | [Latina](README_la.md) | [Lietuvių](README_lt.md) | [Latviešu](README_lv.md) | [Macedonian](README_mk.md) | [Melayu](README_ms.md) | [Norsk bokmål](README_nb.md) | [Nederlands](README_nl.md) | [Norsk nynorsk](README_nn.md) | [Norsk](README_no.md) | [Polski](README_pl.md) | [Português (Brasil)](README_pt-BR.md) | [Português (Portugal)](README_pt-PT.md) | [Română](README_ro.md) | [Русский](README_ru.md) | [Slovenčina](README_sk.md) | [Slovenščina](README_sl.md) | [Shqip](README_sq.md) | [Srpski](README_sr.md) | [Svenska](README_sv.md) | [தமிழ்](README_ta.md) | [తెలుగు](README_te.md) | [ไทย](README_th.md) | [Türkçe](README_tr.md) | [Українська](README_uk.md) | [اردو](README_ur.md) | [Tiếng Việt](README_vi.md) | [繁體中文](README_zh-TW.md) | [中文（简体）](../README.md)

---


> **AI驅動的電子書產生器，讓你輕鬆創建精美的電子書。**

## 快速開始
### 設定環境變數
```
cd backend
copy .env.example .env
```

### 使用 uv 安裝後端依賴

```
cd backend

# 同步安裝所有依賴（自動建立虛擬環境）
uv sync

# 或指定 Python 版本
uv sync --python 3.11
```

### 初始化資料庫
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### 啟動後端服務
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
說明：`uv run` 會自動使用專案虛擬環境中的 Python 執行命令，無需手動啟動環境。

後端將運行在 http://localhost:8000

API 文件位址：http://localhost:8000/docs

### 安裝前端依賴
```
cd frontend
npm install
```

### 啟動前端開發伺服器

```
cd frontend
npm run dev
```
前端將運行在 http://localhost:5173


---

---

## Docker 部署（選擇性）

如果使用 Docker，請確認已安裝 Docker Desktop，然後執行：

```bash
docker-compose up -d
```

這將同時啟動前後端服務。

**注意：** 需要先在 `backend/.env` 中設定好環境變數。


## 支援語言

BookBook 支援以下介面語言：

| 語言 | 代碼 | 語言 | 代碼 |
|------|------|------|------|
| 中文（簡體） | zh-CN | 中文（繁體） | zh-TW |
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

共支援 **82** 種語言。

## 埠說明

| 服務 | 埠 | 說明 |
|------|------|------|
| 前端 (Vite) | 5173 | React 開發伺服器 |
| 後端 (FastAPI) | 8000 | API 服務 |
| P2P 廣播 (UDP) | 47832 | 區域網路節點發現 |
| P2P 書籍同步 (TCP) | 47833 | 書籍資料傳輸 |

**防火牆設定：**
如需使用 P2P 功能，請確保埠 47832（UDP）和 47833（TCP）在區域網路內開放。
