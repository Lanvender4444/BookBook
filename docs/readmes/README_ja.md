# BookBook - AI電子書籍ジェネレーター

## クイックスタート
### 環境変数の設定
```
cd backend
copy .env.example .env
```

### uvでバックエンドの依存関係をインストール

```
cd backend

# すべての依存関係を同期インストール（仮想環境を自動作成）
uv sync

# またはPythonバージョンを指定
uv sync --python 3.11
```

### データベースの初期化
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### バックエンドサービスの起動
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
説明：`uv run`はプロジェクトの仮想環境のPythonを自動的に使用し、手動で環境をアクティブにする必要はありません。

バックエンドは http://localhost:8000 で実行されます

APIドキュメント：http://localhost:8000/docs

### フロントエンドの依存関係をインストール
```
cd frontend
npm install
```

### フロントエンド開発サーバーの起動

```
cd frontend
npm run dev
```
フロントエンドは http://localhost:5173 で実行されます

## クイック起動スクリプト（Windows）

### バックエンドをワンクリックで起動

`start_backend.bat`を作成：
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### フロントエンドをワンクリックで起動

`start_frontend.bat`を作成：
```batch
@echo off
cd frontend
npm run dev
pause
```

### すべてのサービスをワンクリックで起動

`start_all.bat`を作成：
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

## Dockerデプロイメント（オプション）

Dockerを使用する場合は、Docker Desktopがインストールされていることを確認し、以下を実行：

```bash
docker-compose up -d
```

これにより、フロントエンドとバックエンドの両方のサービスが起動します。

**注意：** まず`backend/.env`で環境変数を設定する必要があります。


## サポート言語

BookBookは以下のインターフェース言語をサポートしています：

| 言語 | コード | 言語 | コード |
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

合計 **82** 言語をサポート。

## ポート説明

| サービス | ポート | 説明 |
|------|------|------|
| フロントエンド (Vite) | 5173 | React開発サーバー |
| バックエンド (FastAPI) | 8000 | APIサービス |
| P2Pブロードキャスト (UDP) | 47832 | LANノード検出 |
| P2P書籍同期 (TCP) | 47833 | 書籍データ転送 |

**ファイアウォール設定：**
P2P機能を使用する場合は、ポート47832（UDP）と47833（TCP）がLAN内で開放されていることを確認してください。
