@echo off
cd /d %~dp0
taskkill /IM FotoGalerija.exe /F >nul 2>&1
echo ✅ FotoGalerija je zaustavljena.
pause
