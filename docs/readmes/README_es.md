# BookBook - Generador de eBooks con IA

> **Un generador de eBooks impulsado por IA que te permite crear hermosos ebooks con asistencia de IA.**

## Inicio Rápido
### Configurar Variables de Entorno
```
cd backend
copy .env.example .env
```

### Instalar Dependencias del Backend con uv

```
cd backend

# Sincronizar e instalar todas las dependencias (crea entorno virtual automáticamente)
uv sync

# O especificar versión de Python
uv sync --python 3.11
```

### Inicializar Base de Datos
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Iniciar Servicio Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Nota: `uv run` usa automáticamente Python del entorno virtual del proyecto, no es necesario activarlo manualmente.

El backend se ejecutará en http://localhost:8000

Documentación de la API: http://localhost:8000/docs

### Instalar Dependencias del Frontend
```
cd frontend
npm install
```

### Iniciar Servidor de Desarrollo del Frontend

```
cd frontend
npm run dev
```
El frontend se ejecutará en http://localhost:5173


---

---

## Despliegue con Docker (Opcional)

Si usa Docker, asegúrese de tener Docker Desktop instalado, luego ejecute:

```bash
docker-compose up -d
```

Esto iniciará tanto el frontend como el backend.

**Nota:** Primero debe configurar las variables de entorno en `backend/.env`.


## Idiomas Soportados

BookBook soporta los siguientes idiomas de interfaz:

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

## Descripción de Puertos

| Servicio | Puerto | Descripción |
|------|------|------|
| Frontend (Vite) | 5173 | Servidor de desarrollo React |
| Backend (FastAPI) | 8000 | Servicio API |
| Difusión P2P (UDP) | 47832 | Descubrimiento de nodos LAN |
| Sincronización P2P (TCP) | 47833 | Transferencia de datos de libros |

**Configuración de Firewall:**
Si usa funcionalidades P2P, asegúrese de que los puertos 47832 (UDP) y 47833 (TCP) estén abiertos en su LAN.
