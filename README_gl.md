# BookBook - Xerador de Libros Electrónicos con IA

## Inicio Rápido
### Configurar Variábeis de Contorno
```
cd backend
copy .env.example .env
```

### Instalar Dependencias do Backend con uv

```
cd backend

# Sincronizar e instalar todas as dependencias (crea o contorno virtual automaticamente)
uv sync

# Ou especificar a versión de Python
uv sync --python 3.11
```

### Inicializar a Base de Datos
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Iniciar o Servizo Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Nota: `uv run` usa automaticamente Python do contorno virtual do proxecto, non é necesaria a activación manual.

O backend executarase en http://localhost:8000

Documentación da API: http://localhost:8000/docs

### Instalar Dependencias do Frontend
```
cd frontend
npm install
```

### Iniciar o Servidor de Desenvolvemento Frontend

```
cd frontend
npm run dev
```
O frontend executarase en http://localhost:5173

## Scripts de Inicio Rápido (Windows)

### Iniciar o Backend cun Solo Clic

Crear `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Iniciar o Frontend cun Solo Clic

Crear `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Iniciar Todos os Servizos cun Solo Clic

Crear `start_all.bat`:
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

## Despregue con Docker (Opcional)

Se usa Docker, asegúrese de que Docker Desktop está instalado, logo execute:

```bash
docker-compose up -d
```

Isto iniciará tanto o frontend como o backend.

**Nota:** As variábeis de contorno deben configurarse primeiro en `backend/.env`.


## Idiomas Soportados

BookBook soporta os seguintes idiomas de interface:

| Idioma | Código | Idioma | Código |
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

Total de **82** idiomas soportados.

## Descrición dos Portos

| Servizo | Porto | Descrición |
|------|------|------|
| Frontend (Vite) | 5173 | Servidor de desenvolvemento React |
| Backend (FastAPI) | 8000 | Servizo API |
| Difusión P2P (UDP) | 47832 | Descuberta de nodos LAN |
| Sincronización P2P (TCP) | 47833 | Transferencia de datos de libros |

**Configuración de Cortafuegos:**
Se usa funcionalidades P2P, asegúrese de que os portos 47832 (UDP) e 47833 (TCP) están abertos na súa LAN.
