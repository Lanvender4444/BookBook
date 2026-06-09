# BookBook - Trình tạo Sách điện tử AI

> **Trình tạo sách điện tử AI giúp bạn tạo sách điện tử đẹp mắt với sự hỗ trợ của AI.**

## Bắt đầu nhanh
### Cấu hình Biến Môi trường
```
cd backend
copy .env.example .env
```

### Cài đặt Phụ thuộc Backend với uv

```
cd backend

# Đồng bộ và cài đặt tất cả phụ thuộc (tự động tạo môi trường ảo)
uv sync

# Hoặc chỉ định phiên bản Python
uv sync --python 3.11
```

### Khởi tạo Cơ sở Dữ liệu
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### Khởi động Dịch vụ Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
Ghi chú: `uv run` tự động sử dụng Python từ môi trường ảo của dự án, không cần kích hoạt thủ công.

Backend sẽ chạy tại http://localhost:8000

Tài liệu API: http://localhost:8000/docs

### Cài đặt Phụ thuộc Frontend
```
cd frontend
npm install
```

### Khởi động Máy chủ Phát triển Frontend

```
cd frontend
npm run dev
```
Frontend sẽ chạy tại http://localhost:5173


---

---

## Triển khai Docker (Tùy chọn)

Nếu sử dụng Docker, đảm bảo Docker Desktop đã được cài đặt, sau đó chạy:

```bash
docker-compose up -d
```

Điều này sẽ khởi động cả frontend và backend.

**Lưu ý:** Biến môi trường phải được cấu hình trước trong `backend/.env`.


## Ngôn ngữ được Hỗ trợ

BookBook hỗ trợ các ngôn ngữ giao diện sau:

| Ngôn ngữ | Mã | Ngôn ngữ | Mã |
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

Tổng cộng **82** ngôn ngữ được hỗ trợ.

## Mô tả Cổng

| Dịch vụ | Cổng | Mô tả |
|------|------|------|
| Frontend (Vite) | 5173 | Máy chủ phát triển React |
| Backend (FastAPI) | 8000 | Dịch vụ API |
| P2P Broadcast (UDP) | 47832 | Phát hiện nút LAN |
| P2P Đồng bộ Sách (TCP) | 47833 | Truyền dữ liệu sách |

**Cài đặt Tường lửa:**
Nếu sử dụng tính năng P2P, đảm bảo cổng 47832 (UDP) và 47833 (TCP) được mở trên LAN của bạn.
