# BookBook 一键打包脚本
# 用法: 在项目根目录执行  .\build.ps1
#       仅重打后端:        .\build.ps1 -BackendOnly
#       跳过后端(已打过):  .\build.ps1 -SkipBackend
param(
    [switch]$BackendOnly,
    [switch]$SkipBackend
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Fail($msg) { Write-Host "[错误] $msg" -ForegroundColor Red; exit 1 }

# ---------- 0. 环境检查 ----------
Step "检查环境"
if (-not (Get-Command rustc -ErrorAction SilentlyContinue)) { Fail "未找到 rustc，请安装 Rust: https://rustup.rs" }
if (-not (Get-Command npm -ErrorAction SilentlyContinue))   { Fail "未找到 npm，请安装 Node.js >= 18" }
if (-not (Test-Path "$Root\config.json")) { Fail "项目根目录缺少 config.json" }

$TRIPLE = (rustc -vV | Select-String "host:").ToString().Split(" ")[1].Trim()
Write-Host "Target triple: $TRIPLE"

$BinDir = "$Root\frontend\src-tauri\binaries"
$SidecarExe = "$BinDir\backend-$TRIPLE.exe"

# ---------- 1. 打包 Python 后端 ----------
if (-not $SkipBackend) {
    Step "打包 Python 后端 (PyInstaller)"
    $Venv = "$Root\backend\.venv\Scripts"
    if (-not (Test-Path "$Venv\python.exe")) { Fail "未找到 backend\.venv，请先创建虚拟环境并安装依赖" }
    if (-not (Test-Path "$Venv\pyinstaller.exe")) {
        Write-Host "venv 中未安装 PyInstaller，正在安装..."
        & "$Venv\pip.exe" install pyinstaller
    }

    Push-Location "$Root\backend"
    try {
        # 先杀掉可能残留的旧后端进程，否则 dist\backend.exe 被占用会导致覆盖失败
        Get-Process backend -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        & "$Venv\pyinstaller.exe" --onefile --noconsole --name backend --clean -y main.py
        if ($LASTEXITCODE -ne 0) { Fail "PyInstaller 打包失败" }
    } finally { Pop-Location }

    Step "复制 sidecar 到 Tauri binaries 目录"
    New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
    Copy-Item "$Root\backend\dist\backend.exe" $SidecarExe -Force
    Write-Host "已生成: $SidecarExe"
}

if ($BackendOnly) { Write-Host "`n后端打包完成 (BackendOnly 模式)" -ForegroundColor Green; exit 0 }

# ---------- 2. 检查 sidecar 是否就位 ----------
if (-not (Test-Path $SidecarExe)) {
    Fail "缺少 sidecar: $SidecarExe`n请先不带 -SkipBackend 运行一次"
}

# ---------- 3. 构建 Tauri 应用 ----------
Step "安装前端依赖"
Push-Location "$Root\frontend"
try {
    if (-not (Test-Path "node_modules")) { npm install; if ($LASTEXITCODE -ne 0) { Fail "npm install 失败" } }

    Step "构建 Tauri 应用 (npm run build + cargo build + 打包)"
    npx tauri build
    if ($LASTEXITCODE -ne 0) { Fail "tauri build 失败" }
} finally { Pop-Location }

# ---------- 4. 输出产物位置 ----------
Step "打包完成"
$Bundle = "$Root\frontend\src-tauri\target\release\bundle"
Get-ChildItem -Recurse $Bundle -Include *.exe, *.msi -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  产物: $($_.FullName)" -ForegroundColor Green
}
