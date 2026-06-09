# BookBook - Generator eBooków AI

## Szybki Start
### Konfiguracja Zmiennych Środowiskowych
```
cd backend
copy .env.example .env
```

### Instalacja Zależności Backendu za pomocą uv

```
cd backend

# Synchronizacja i instalacja wszystkich zależności (automatycznie tworzy środowisko wirtualne)
uv sync

# Lub określenie wersji Python
uv sync --python 3.11
```

### Inicjalizacja Bazy Danych
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Uruchomienie Usługi Backendu
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Uwaga: `uv run` automatycznie używa Python ze środowiska wirtualnego projektu, nie wymaga ręcznej aktywacji.

Backend będzie działał pod adresem http://localhost:8000

Dokumentacja API: http://localhost:8000/docs

### Instalacja Zależności Frontendu
```
cd frontend
npm install
```

### Uruchomienie Serwera Deweloperskiego Frontendu

```
cd frontend
npm run dev
```
Frontend będzie działał pod adresem http://localhost:5173

## Skrypty Szybkiego Uruchamiania (Windows)

### Uruchom Backend jednym kliknięciem

Utwórz `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Uruchom Frontend jednym kliknięciem

Utwórz `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Uruchom Wszystkie Usługi jednym kliknięciem

Utwórz `start_all.bat`:
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

## Wdrożenie Docker (Opcjonalne)

Jeśli korzystasz z Docker, upewnij się, że Docker Desktop jest zainstalowany, a następnie uruchom:

```bash
docker-compose up -d
```

Uruchomi to zarówno frontend, jak i backend.

**Uwaga:** Zmienne środowiskowe muszą najpierw zostać skonfigurowane w `backend/.env`.


## Obsługiwane Języki

BookBook obsługuje następujące języki interfejsu:

| Język | Kod | Język | Kod |
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

Łącznie **82** obsługiwanych języków.

## Opis Portów

| Usługa | Port | Opis |
|------|------|------|
| Frontend (Vite) | 5173 | Serwer deweloperski React |
| Backend (FastAPI) | 8000 | Usługa API |
| P2P Broadcast (UDP) | 47832 | Odkrywanie węzłów LAN |
| P2P Book Sync (TCP) | 47833 | Transfer danych książek |

**Ustawienia Zapory:**
Jeśli korzystasz z funkcji P2P, upewnij się, że porty 47832 (UDP) i 47833 (TCP) są otwarte w Twojej sieci LAN.
