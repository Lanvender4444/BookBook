# BookBook - AI 전자책 생성기

> **AI 기반 전자책 생성기 - AI의 도움으로 아름다운 전자책을 쉽게 만들 수 있습니다.**

## 빠른 시작
### 환경 변수 설정
```
cd backend
copy .env.example .env
```

### uv로 백엔드 의존성 설치

```
cd backend

# 모든 의존성 동기화 설치 (가상 환경 자동 생성)
uv sync

# 또는 Python 버전 지정
uv sync --python 3.11
```

### 데이터베이스 초기화
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### 백엔드 서비스 시작
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
참고: `uv run`은 프로젝트 가상 환경의 Python을 자동으로 사용하며 수동으로 환경을 활성화할 필요가 없습니다.

백엔드는 http://localhost:8000 에서 실행됩니다

API 문서: http://localhost:8000/docs

### 프론트엔드 의존성 설치
```
cd frontend
npm install
```

### 프론트엔드 개발 서버 시작

```
cd frontend
npm run dev
```
프론트엔드는 http://localhost:5173 에서 실행됩니다


---

---

## Docker 배포 (선택사항)

Docker를 사용하는 경우 Docker Desktop이 설치되어 있는지 확인하고 다음을 실행합니다:

```bash
docker-compose up -d
```

이것은 프론트엔드와 백엔드 서비스를 동시에 시작합니다.

**참고:** 먼저 `backend/.env`에서 환경 변수를 구성해야 합니다.


## 지원 언어

BookBook은 다음 인터페이스 언어를 지원합니다:

| 언어 | 코드 | 언어 | 코드 |
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

총 **82**개 언어 지원.

## 포트 설명

| 서비스 | 포트 | 설명 |
|------|------|------|
| 프론트엔드 (Vite) | 5173 | React 개발 서버 |
| 백엔드 (FastAPI) | 8000 | API 서비스 |
| P2P 브로드캐스트 (UDP) | 47832 | LAN 노드 검색 |
| P2P 도서 동기화 (TCP) | 47833 | 도서 데이터 전송 |

**방화벽 설정:**
P2P 기능을 사용하는 경우 포트 47832 (UDP) 및 47833 (TCP)가 LAN에서 열려 있는지 확인하세요.
