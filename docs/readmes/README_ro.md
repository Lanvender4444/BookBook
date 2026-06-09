# BookBook - Generator de eBooks AI

> **Un generator de eBooks cu IA care vă permite să creați eBooks frumoase cu asistență IA.**

## Pornire Rapidă
### Configurarea Variabilelor de Mediu
```
cd backend
copy .env.example .env
```

### Instalarea Dependențelor Backend cu uv

```
cd backend

# Sincronizarea și instalarea tuturor dependențelor (creează automat mediul virtual)
uv sync

# Sau specificarea versiunii Python
uv sync --python 3.11
```

### Inițializarea Bazei de Date
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Pornirea Serviciului Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Notă: `uv run` folosește automat Python din mediul virtual al proiectului, nu este necesară activarea manuală.

Backend-ul va rula la http://localhost:8000

Documentație API: http://localhost:8000/docs

### Instalarea Dependențelor Frontend
```
cd frontend
npm install
```

### Pornirea Serverului de Dezvoltare Frontend

```
cd frontend
npm run dev
```
Frontend-ul va rula la http://localhost:5173


---

---

## Implementare Docker (Opțională)

Dacă utilizați Docker, asigurați-vă că Docker Desktop este instalat, apoi rulați:

```bash
docker-compose up -d
```

Aceasta va porni atât frontend-ul, cât și backend-ul.

**Notă:** Variabilele de mediu trebuie mai întâi configurate în `backend/.env`.


## Limbi Suportate

BookBook suportă următoarele limbi de interfață:

| Limbă | Cod | Limbă | Cod |
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

Total **82** limbi suportate.

## Descrierea Porturilor

| Serviciu | Port | Descriere |
|------|------|------|
| Frontend (Vite) | 5173 | Server de dezvoltare React |
| Backend (FastAPI) | 8000 | Serviciu API |
| P2P Broadcast (UDP) | 47832 | Descoperire noduri LAN |
| P2P Book Sync (TCP) | 47833 | Transfer date cărți |

**Setări Firewall:**
Dacă utilizați funcționalități P2P, asigurați-vă că porturile 47832 (UDP) și 47833 (TCP) sunt deschise în rețeaua dvs. LAN.
