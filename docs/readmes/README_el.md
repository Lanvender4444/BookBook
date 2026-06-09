# BookBook - AI eBook Γεννήτρια

## Γρήγορη Εκκίνηση
### Ρύθμιση Μεταβλητών Περιβάλλοντος
```
cd backend
copy .env.example .env
```

### Εγκατάσταση Εξαρτήσεων Backend με uv

```
cd backend

# Συγχρονισμός και εγκατάσταση όλων των εξαρτήσεων (δημιουργεί εικονικό περιβάλλον αυτόματα)
uv sync

# Ή καθορισμός έκδοσης Python
uv sync --python 3.11
```

### Αρχικοποίηση Βάσης Δεδομένων
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Εκκίνηση Υπηρεσίας Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Σημείωση: Το `uv run` χρησιμοποιεί αυτόματα το Python από το εικονικό περιβάλλον του έργου, δεν απαιτείται χειροκίνητη ενεργοποίηση.

Το Backend θα εκτελείται στο http://localhost:8000

Τεκμηρίωση API: http://localhost:8000/docs

### Εγκατάσταση Εξαρτήσεων Frontend
```
cd frontend
npm install
```

### Εκκίνηση Διακομιστή Ανάπτυξης Frontend

```
cd frontend
npm run dev
```
Το Frontend θα εκτελείται στο http://localhost:5173

## Σενάρια Γρήγορης Εκκίνησης (Windows)

### Εκκίνηση Backend με ένα κλικ

Δημιουργία `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Εκκίνηση Frontend με ένα κλικ

Δημιουργία `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Εκκίνηση Όλων των Υπηρεσιών με ένα κλικ

Δημιουργία `start_all.bat`:
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

## Ανάπτυξη Docker (Προαιρετική)

Αν χρησιμοποιείτε Docker, βεβαιωθείτε ότι το Docker Desktop είναι εγκατεστημένο, στη συνέχεια εκτελέστε:

```bash
docker-compose up -d
```

Αυτό θα ξεκινήσει τόσο το Frontend όσο και το Backend.

**Σημείωση:** Οι μεταβλητές περιβάλλοντος πρέπει πρώτα να ρυθμιστούν στο `backend/.env`.


## Υποστηριζόμενες Γλώσσες

Το BookBook υποστηρίζει τις ακόλουθες γλώσσες διεπαφής:

| Γλώσσα | Κωδικός | Γλώσσα | Κωδικός |
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

Σύνολο **82** υποστηριζόμενων γλωσσών.

## Περιγραφή Θυρών

| Υπηρεσία | Θύρα | Περιγραφή |
|------|------|------|
| Frontend (Vite) | 5173 | Διακομιστής ανάπτυξης React |
| Backend (FastAPI) | 8000 | Υπηρεσία API |
| P2P Broadcast (UDP) | 47832 | Ανακάλυψη κόμβων LAN |
| P2P Book Sync (TCP) | 47833 | Μεταφορά δεδομένων βιβλίων |

**Ρυθμίσεις Firewall:**
Αν χρησιμοποιείτε λειτουργίες P2P, βεβαιωθείτε ότι οι θύρες 47832 (UDP) και 47833 (TCP) είναι ανοιχτές στο LAN σας.
