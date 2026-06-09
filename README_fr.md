# BookBook - Générateur de Livres Électroniques IA

## Démarrage Rapide
### Configurer les Variables d'Environnement
```
cd backend
copy .env.example .env
```

### Installer les Dépendances Backend avec uv

```
cd backend

# Synchroniser et installer toutes les dépendances (crée l'environnement virtuel automatiquement)
uv sync

# Ou spécifier la version de Python
uv sync --python 3.11
```

### Initialiser la Base de Données
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Démarrer le Service Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Note : `uv run` utilise automatiquement Python de l'environnement virtuel du projet, pas besoin d'activer manuellement.

Le backend fonctionnera sur http://localhost:8000

Documentation API : http://localhost:8000/docs

### Installer les Dépendances Frontend
```
cd frontend
npm install
```

### Démarrer le Serveur de Développement Frontend

```
cd frontend
npm run dev
```
Le frontend fonctionnera sur http://localhost:5173

## Scripts de Démarrage Rapide (Windows)

### Démarrer le Backend en Un Clic

Créer `start_backend.bat` :
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Démarrer le Frontend en Un Clic

Créer `start_frontend.bat` :
```batch
@echo off
cd frontend
npm run dev
pause
```

### Démarrer Tous les Services en Un Clic

Créer `start_all.bat` :
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

## Déploiement Docker (Optionnel)

Si vous utilisez Docker, assurez-vous que Docker Desktop est installé, puis exécutez :

```bash
docker-compose up -d
```

Cela démarrera à la fois les services frontend et backend.

**Note :** Les variables d'environnement doivent d'abord être configurées dans `backend/.env`.


## Langues Supportées

BookBook supporte les langues d'interface suivantes :

| Langue | Code | Langue | Code |
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

Total de **82** langues supportées.

## Description des Ports

| Service | Port | Description |
|------|------|------|
| Frontend (Vite) | 5173 | Serveur de développement React |
| Backend (FastAPI) | 8000 | Service API |
| Diffusion P2P (UDP) | 47832 | Découverte de nœuds LAN |
| Synchronisation P2P (TCP) | 47833 | Transfert de données de livres |

**Paramètres Pare-feu :**
Si vous utilisez les fonctionnalités P2P, assurez-vous que les ports 47832 (UDP) et 47833 (TCP) sont ouverts sur votre LAN.
