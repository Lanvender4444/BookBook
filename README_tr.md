# BookBook - AI eBook Oluşturucu

## Hızlı Başlangıç
### Çevresel Değişkenleri Yapılandırın
```
cd backend
copy .env.example .env
```

### uv ile Backend Bağımlılıklarını Yükleyin

```
cd backend

# Tüm bağımlılıkları senkronize edin ve yükleyin (sanal ortamı otomatik oluşturur)
uv sync

# Veya Python sürümünü belirtin
uv sync --python 3.11
```

### Veritabanını Başlatın
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend Servisini Başlatın
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Not: `uv run` projenin sanal ortamındaki Python'u otomatik kullanır, manuel aktivasyon gerekmez.

Backend http://localhost:8000 adresinde çalışacaktır

API dokümantasyonu: http://localhost:8000/docs

### Frontend Bağımlılıklarını Yükleyin
```
cd frontend
npm install
```

### Frontend Geliştirme Sunucusunu Başlatın

```
cd frontend
npm run dev
```
Frontend http://localhost:5173 adresinde çalışacaktır

## Hızlı Başlatma Betikleri (Windows)

### Backend'i Tek Tıklamayla Başlatın

`start_backend.bat` oluşturun:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Frontend'i Tek Tıklamayla Başlatın

`start_frontend.bat` oluşturun:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Tüm Servisleri Tek Tıklamayla Başlatın

`start_all.bat` oluşturun:
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

## Docker Dağıtımı (İsteğe Bağlı)

Docker kullanıyorsanız, Docker Desktop'ın yüklü olduğundan emin olun, ardından çalıştırın:

```bash
docker-compose up -d
```

Bu, hem frontend hem de backend servislerini başlatacaktır.

**Not:** Önce `backend/.env` dosyasında çevresel değişkenleri yapılandırmanız gerekir.


## Desteklenen Diller

BookBook aşağıdaki arayüz dillerini destekler:

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

Toplam **82** desteklenen dil.

## Port Açıklaması

| Servis | Port | Açıklama |
|------|------|------|
| Frontend (Vite) | 5173 | React geliştirme sunucusu |
| Backend (FastAPI) | 8000 | API servisi |
| P2P Yayın (UDP) | 47832 | LAN düğüm keşfi |
| P2P Kitap Senkronizasyonu (TCP) | 47833 | Kitap veri aktarımı |

**Güvenlik Duvarı Ayarları:**
P2P özelliklerini kullanıyorsanız, 47832 (UDP) ve 47833 (TCP) portlarının LAN'ınızda açık olduğundan emin olun.
