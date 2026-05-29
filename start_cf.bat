@echo off
title WeCom Bridge
cd /d "%~dp0"

echo Starting Flask server...
start "Flask" /B python server.py > server.log 2>&1
timeout /t 3 > nul

echo.
echo Starting cloudflared tunnel...
echo.
cloudflared.exe tunnel --url http://localhost:8080
pause
