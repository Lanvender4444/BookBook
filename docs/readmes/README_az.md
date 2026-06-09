# BookBook - AI eBook Yaradıcı

## Sürətli Başlanğıc
### Ətraf Mühit Dəyişənlərini Konfiqurasiya Edin
```
cd backend
copy .env.example .env
```

### uv ilə Backend Asılılıqlarını Quraşdırın

```
cd backend

# Bütün asılılıqları sinxronlaşdırın və quraşdırın (virtual mühiti avtomatik yaradır)
uv sync

# Və ya Python versiyasını göstərin
uv sync --python 3.11
```

### Verilənlər Bazasını Başladın
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend Xidmətini Başladın
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Qeyd: `uv run` avtomatik olaraq layihənin virtual mühitindən Python istifadə edir, əl ilə aktivləşdirmə lazımdır.

Backend http://localhost:8000 ünvanında işləyəcək

API sənədləri: http://localhost:8000/docs

### Frontend Asılılıqlarını Quraşdırın
```
cd frontend
npm install
```

### Frontend Tərtibat Serverini Başladın

```
cd frontend
npm run dev
```
Frontend http://localhost:5173 ünvanında işləyəcək

## Sürətli Başlanğıc Skriptləri (Windows)

### Backend-i Bir Kliklə Başladın

`start_backend.bat` yaradın:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Frontend-i Bir Kliklə Başladın

`start_frontend.bat` yaradın:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Bütün Xidmətləri Bir Kliklə Başladın

`start_all.bat` yaradın:
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

## Docker İstifadəsi (İxtiyari)

Docker istifadə edirsinizsə, Docker Desktop-ın quraşdırıldığına əmin olun, sonra işə salın:

```bash
docker-compose up -d
```

Bu, həm frontend, həm də backend xidmətlərini işə salacaq.

**Qeyd:** Əvvəlcə `backend/.env` faylında ətraf mühit dəyişənləri konfiqurasiya edilməlidir.


## Dəstəklənən Dillər

BookBook aşağıdakı interfeys dillərini dəstəkləyir:

| Dil | Kod | Dil | Kod |
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

Cəmi **82** dəstəklənən dil.

## Port Təsviri

| Xidmət | Port | Təsvir |
|------|------|------|
| Frontend (Vite) | 5173 | React tərtibat serveri |
| Backend (FastAPI) | 8000 | API xidməti |
| P2P Yayım (UDP) | 47832 | LAN node aşkarlanması |
| P2P Kitab Sinxronizasiyası (TCP) | 47833 | Kitab datalarının ötürülməsi |

**Firewall Parametrləri:**
P2P funksiyalarından istifadə edirsinizsə, portların 47832 (UDP) və 47833 (TCP) LAN-da açıq olduğundan əmin olun.
