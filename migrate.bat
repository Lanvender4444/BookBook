@echo off
echo Killing running backend processes...
taskkill /F /IM backend.exe >nul 2>&1
taskkill /F /IM app.exe >nul 2>&1
taskkill /F /IM BookBook.exe >nul 2>&1
timeout /t 1 /nobreak >nul
"%~dp0backend\.venv\Scripts\python.exe" "%~dp0migrate_data.py"
pause
