# BookBook 一键打包脚本
# 用法: 在项目根目录执行  powershell -ExecutionPolicy Bypass -File build.ps1

# 如果之前执行过开发版，需要手动停止 后端进程
# taskkill /F /IM backend.exe

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

Write-Host "=== [0/5] 清理残留的 backend.exe 进程 ===" -ForegroundColor Cyan
# 残留进程会锁住 SQLite / 占用端口，也会导致 PyInstaller 无法覆盖 exe
Get-Process backend -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500

Write-Host "=== [1/5] 清理旧构建产物 ===" -ForegroundColor Cyan
# 清掉 PyInstaller 缓存与旧 sidecar，避免“改了代码却打出旧包”
foreach ($p in @("$Root\backend\build", "$Root\backend\dist")) {
    if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}
if (Test-Path "$Root\frontend\src-tauri\binaries") {
    # 删除所有旧的 backend-<triple>.exe，防止换工具链后旧 triple 的包被一起打进去
    Get-ChildItem "$Root\frontend\src-tauri\binaries" -Filter "backend-*.exe" -ErrorAction SilentlyContinue |
        Remove-Item -Force -ErrorAction SilentlyContinue
}

Write-Host "=== [2/5] PyInstaller 打包后端 ===" -ForegroundColor Cyan
Push-Location "$Root\backend"
& ".\.venv\Scripts\Activate.ps1"

# 确保后端依赖齐全（缺依赖时 exe 仍能打出，但运行时才崩）
if (Test-Path ".\requirements.txt") {
    Write-Host "安装/校验后端依赖 (requirements.txt)..." -ForegroundColor DarkGray
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { Pop-Location; throw "依赖安装失败" }
}
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "pyinstaller 未安装，正在安装..." -ForegroundColor Yellow
    pip install pyinstaller
}

# --collect-all：把 python-docx 的 default.docx 模板、reportlab / ebooklib / PIL 的数据文件
# 一并打进去，否则 DOCX / EPUB / PDF 导出会在打包版里报“缺文件”（dev 正常、装好的包崩）
# --clean / --noconfirm：清 PyInstaller 缓存并覆盖产物，避免残留旧字节码
pyinstaller --onefile --noconsole --name backend `
    --collect-all docx `
    --collect-all ebooklib `
    --collect-all reportlab `
    --collect-all PIL `
    --hidden-import uvicorn `
    --clean --noconfirm `
    main.py
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "PyInstaller 打包失败" }
Pop-Location

# 校验产物确实生成
$BackendExe = "$Root\backend\dist\backend.exe"
if (-not (Test-Path $BackendExe)) { throw "未找到 $BackendExe，PyInstaller 可能失败" }

Write-Host "=== [3/5] 复制 sidecar 到 Tauri binaries ===" -ForegroundColor Cyan
$Triple = (rustc -vV | Select-String "host:" | ForEach-Object { ($_ -split " ")[1] }).Trim()
if ([string]::IsNullOrWhiteSpace($Triple)) { throw "无法获取 rustc target triple，请确认已安装 Rust 工具链" }
Write-Host "Target triple: $Triple"
New-Item -ItemType Directory -Force -Path "$Root\frontend\src-tauri\binaries" | Out-Null
Copy-Item -Path $BackendExe `
          -Destination "$Root\frontend\src-tauri\binaries\backend-$Triple.exe" -Force

Write-Host "=== [4/5] 构建 Tauri 应用 ===" -ForegroundColor Cyan
Push-Location "$Root\frontend"
npm install
npx tauri build
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "Tauri 打包失败" }
Pop-Location

Write-Host "=== [5/5] 完成 ===" -ForegroundColor Green
Write-Host "安装包: frontend\src-tauri\target\release\bundle\nsis\"
Write-Host "提示: 重装前请先卸载旧版本，并确认任务管理器中没有残留的 backend.exe"
