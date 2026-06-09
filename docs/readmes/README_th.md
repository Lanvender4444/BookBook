# BookBook - เครื่องสร้างหนังสืออิเล็กทรอนิกส์ AI

## เริ่มต้นใช้งาน
### ตั้งค่าตัวแปรสภาพแวดล้อม
```
cd backend
copy .env.example .env
```

### ติดตั้ง Dependencies ของ Backend ด้วย uv

```
cd backend

# ซิงค์และติดตั้ง dependencies ทั้งหมด (สร้าง virtual environment โดยอัตโนมัติ)
uv sync

# หรือระบุเวอร์ชัน Python
uv sync --python 3.11
```

### เริ่มต้นฐานข้อมูล
```cd backend
uv run python -c "from database import init_db; init_db()"

```

### เริ่มต้นบริการ Backend
```
cd backend
uv run uvicorn main:app --reload --port 8000
```
หมายเหตุ: `uv run` จะใช้ Python จาก virtual environment ของโปรเจคโดยอัตโนมัติ ไม่ต้องเปิดใช้งานด้วยตนเอง

Backend จะทำงานที่ http://localhost:8000

เอกสาร API: http://localhost:8000/docs

### ติดตั้ง Dependencies ของ Frontend
```
cd frontend
npm install
```

### เริ่มต้นเซิร์ฟเวอร์พัฒนา Frontend

```
cd frontend
npm run dev
```
Frontend จะทำงานที่ http://localhost:5173

## สคริปต์เริ่มต้นใช้งาน (Windows)

### เริ่มต้น Backend ด้วยคลิกเดียว

สร้าง `start_backend.bat`:
```batch
@echo off
cd backend
uv run uvicorn main:app --reload --port 8000
pause
```

### เริ่มต้น Frontend ด้วยคลิกเดียว

สร้าง `start_frontend.bat`:
```batch
@echo off
cd frontend
npm run dev
pause
```

### เริ่มต้นทุกบริการด้วยคลิกเดียว

สร้าง `start_all.bat`:
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

## การ部署 ด้วย Docker (ทางเลือก)

หากใช้ Docker ให้แน่ใจว่า Docker Desktop ได้ติดตั้งแล้ว จากนั้นรัน:

```bash
docker-compose up -d
```

คำสั่งนี้จะเริ่มต้นทั้ง frontend และ backend

**หมายเหตุ:** ต้องตั้งค่าตัวแปรสภาพแวดล้อมใน `backend/.env` ก่อน


## ภาษาที่รองรับ

BookBook รองรับภาษาอินเทอร์เฟซดังต่อไปนี้:

| ภาษา | รหัส | ภาษา | รหัส |
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

รวมทั้งหมด **82** ภาษาที่รองรับ

## คำอธิบายพอร์ต

| บริการ | พอร์ต | คำอธิบาย |
|------|------|------|
| Frontend (Vite) | 5173 | เซิร์ฟเวอร์พัฒนา React |
| Backend (FastAPI) | 8000 | บริการ API |
| P2P Broadcast (UDP) | 47832 | การค้นหาโหนด LAN |
| P2P Book Sync (TCP) | 47833 | การถ่ายโอนข้อมูลหนังสือ |

**การตั้งค่า Firewall:**
หากใช้ฟีเจอร์ P2P ให้แน่ใจว่าพอร์ต 47832 (UDP) และ 47833 (TCP) เปิดอยู่ใน LAN ของคุณ
