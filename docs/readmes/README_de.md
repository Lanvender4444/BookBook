# BookBook - KI-E-Book-Generator

> **Ein KI-gestützter eBook-Generator, mit dem Sie schöne eBooks mit KI-Unterstützung erstellen können.**

## Schnellstart
### Umgebungsvariablen Konfigurieren
```
cd backend
copy .env.example .env
```

### Backend-Abhängigkeiten mit uv Installieren

```
cd backend

# Alle Abhängigkeiten synchronisieren und installieren (erstellt virtuelle Umgebung automatisch)
uv sync

# Oder Python-Version angeben
uv sync --python 3.11
```

### Datenbank Initialisieren
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Backend-Dienst Starten
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Hinweis: `uv run` verwendet automatisch Python aus der virtuellen Umgebung des Projekts, keine manuelle Aktivierung erforderlich.

Das Backend läuft unter http://localhost:8000

API-Dokumentation: http://localhost:8000/docs

### Frontend-Abhängigkeiten Installieren
```
cd frontend
npm install
```

### Frontend-Entwicklungsserver Starten

```
cd frontend
npm run dev
```
Das Frontend läuft unter http://localhost:5173


---

---

## Docker-Bereitstellung (Optional)

Wenn Sie Docker verwenden, stellen Sie sicher, dass Docker Desktop installiert ist, und führen Sie dann aus:

```bash
docker-compose up -d
```

Dies startet sowohl den Frontend- als auch den Backend-Dienst.

**Hinweis:** Die Umgebungsvariablen müssen zuerst in `backend/.env` konfiguriert werden.


## Unterstützte Sprachen

BookBook unterstützt die folgenden Interface-Sprachen:

| Sprache | Code | Sprache | Code |
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

Insgesamt **82** unterstützte Sprachen.

## Port-Beschreibung

| Dienst | Port | Beschreibung |
|------|------|------|
| Frontend (Vite) | 5173 | React-Entwicklungsserver |
| Backend (FastAPI) | 8000 | API-Dienst |
| P2P-Broadcast (UDP) | 47832 | LAN-Knotenerkennung |
| P2P-Buch-Synchronisation (TCP) | 47833 | Buchdatenübertragung |

**Firewall-Einstellungen:**
Wenn Sie P2P-Funktionen verwenden, stellen Sie sicher, dass die Ports 47832 (UDP) und 47833 (TCP) in Ihrem LAN geöffnet sind.
