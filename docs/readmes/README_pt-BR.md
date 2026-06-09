# BookBook - Gerador de eBooks com IA

## Início Rápido
### Configurar Variáveis de Ambiente
```
cd backend
copy .env.example .env
```

### Instalar Dependências do Backend com uv

```
cd backend

# Sincronizar e instalar todas as dependências (cria ambiente virtual automaticamente)
uv sync

# Ou especificar versão do Python
uv sync --python 3.11
```

### Inicializar Banco de Dados
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Iniciar Serviço Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Nota: `uv run` usa automaticamente o Python do ambiente virtual do projeto, sem necessidade de ativação manual.

O backend rodará em http://localhost:8000

Documentação da API: http://localhost:8000/docs

### Instalar Dependências do Frontend
```
cd frontend
npm install
```

### Iniciar Servidor de Desenvolvimento do Frontend

```
cd frontend
npm run dev
```
O frontend rodará em http://localhost:5173

## Scripts de Início Rápido (Windows)

### Iniciar Backend com Um Clique

Criar `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### Iniciar Frontend com Um Clique

Criar `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### Iniciar Todos os Serviços com Um Clique

Criar `start_all.bat`:
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

## Implantação com Docker (Opcional)

Se você usa Docker, certifique-se de que o Docker Desktop está instalado, depois execute:

```bash
docker-compose up -d
```

Isso iniciará tanto o frontend quanto o backend.

**Nota:** As variáveis de ambiente devem ser configuradas primeiro em `backend/.env`.


## Idiomas Suportados

BookBook suporta os seguintes idiomas de interface:

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

Total de **82** idiomas suportados.

## Descrição das Portas

| Serviço | Porta | Descrição |
|------|------|------|
| Frontend (Vite) | 5173 | Servidor de desenvolvimento React |
| Backend (FastAPI) | 8000 | Serviço API |
| Broadcast P2P (UDP) | 47832 | Descoberta de nós LAN |
| Sincronização P2P (TCP) | 47833 | Transferência de dados de livros |

**Configurações de Firewall:**
Se você usa funcionalidades P2P, certifique-se de que as portas 47832 (UDP) e 47833 (TCP) estão abertas na sua LAN.
