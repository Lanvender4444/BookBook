# BookBook 一键打包脚本
# 用法: 在项目根目录执行  powershell -ExecutionPolicy Bypass -File build.ps1

# 如果之前执行过开发版，需要手动停止 后端进程
# taskkill /F /IM backend.exe

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

Write-Host "=== [0/4] 清理残留的 backend.exe 进程 ===" -ForegroundColor Cyan
# 残留进程会锁住 SQLite / 占用端口，也会导致 PyInstaller 无法覆盖 exe
Get-Process backend -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500

Write-Host "=== [1/4] PyInstaller 打包后端 ===" -ForegroundColor Cyan
Push-Location "$Root\backend"
& ".\.venv\Scripts\Activate.ps1"
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "pyinstaller 未安装，正在安装..." -ForegroundColor Yellow
    pip install pyinstaller
}

pyinstaller --onefile --noconsole --name backend main.py
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "PyInstaller 打包失败" }
Pop-Location

Write-Host "=== [2/4] 复制 sidecar 到 Tauri binaries ===" -ForegroundColor Cyan
$Triple = (rustc -vV | Select-String "host:" | ForEach-Object { ($_ -split " ")[1] }).Trim()
Write-Host "Target triple: $Triple"
New-Item -ItemType Directory -Force -Path "$Root\frontend\src-tauri\binaries" | Out-Null
Copy-Item -Path "$Root\backend\dist\backend.exe" `
          -Destination "$Root\frontend\src-tauri\binaries\backend-$Triple.exe" -Force

Write-Host "=== [3/4] 构建 Tauri 应用 ===" -ForegroundColor Cyan
Push-Location "$Root\frontend"
npm install
npx tauri build
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "Tauri 打包失败" }
Pop-Location

Write-Host "=== [4/4] 完成 ===" -ForegroundColor Green
Write-Host "安装包: frontend\src-tauri\target\release\bundle\nsis\"
Write-Host "提示: 重装前请先卸载旧版本，并确认任务管理器中没有残留的 backend.exe"
