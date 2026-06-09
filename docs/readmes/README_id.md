# BookBook - Generator eBook AI

## Memulai Cepat
### Konfigurasi Variabel Lingkungan
```
cd backend
copy .env.example .env
```

### Instal Dependensi Backend dengan uv

```
cd backend

# Sinkronkan dan instal semua dependensi (membuat virtual environment secara otomatis)
uv sync

# Atau tentukan versi Python
uv sync --python 3.11
```

### Inisialisasi Database
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Mulai Layanan Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Catatan: `uv run` secara otomatis menggunakan Python dari virtual environment proyek, tidak perlu aktivasi manual.

Backend akan berjalan di http://localhost:8000

Dokumentasi API: http://localhost:8000/docs

### Instal Dependensi Frontend
```
cd frontend
npm install
```

### Mulai Server Pengembangan Frontend

```
cd frontend
npm run dev
```
Frontend akan berjalan di http://localhost:5173

## Skrip Memulai Cepat (Windows)

### Mulai Backend dengan Satu Klik

Buat `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Mulai Frontend dengan Satu Klik

Buat `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Mulai Semua Layanan dengan Satu Klik

Buat `start_all.bat`:
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

## Deploy dengan Docker (Opsional)

Jika menggunakan Docker, pastikan Docker Desktop sudah terinstal, lalu jalankan:

```bash
docker-compose up -d
```

Ini akan memulai layanan frontend dan backend.

**Catatan:** Variabel lingkungan harus dikonfigurasi terlebih dahulu di `backend/.env`.


## Bahasa yang Didukung

BookBook mendukung bahasa antarmuka berikut:

| Bahasa | Kode | Bahasa | Kode |
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

Total **82** bahasa yang didukung.

## Deskripsi Port

| Layanan | Port | Deskripsi |
|------|------|------|
| Frontend (Vite) | 5173 | Server pengembangan React |
| Backend (FastAPI) | 8000 | Layanan API |
| P2P Broadcast (UDP) | 47832 | Penemuan node LAN |
| P2P Book Sync (TCP) | 47833 | Transfer data buku |

**Pengaturan Firewall:**
Jika menggunakan fitur P2P, pastikan port 47832 (UDP) dan 47833 (TCP) terbuka di LAN Anda.
