@echo off
setlocal
cd /d %~dp0

echo Pokrecem FotoGaleriju...
start "" "%~dp0FotoGalerija.exe"

REM sacekaj malo da server krene
timeout /t 3 >nul

REM pronadji IPv4 adresu racunara
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /R /C:"IPv4 Address"') do (
    set IP=%%A
)
set IP=%IP: =%
set IP=%IP%

echo.
echo ========================================
echo  LAN adresa vase galerije:
echo      http://%IP%:5000
echo ========================================
echo.

REM otvori lokalno i LAN adresu
start "" "http://localhost:5000"
start "" "http://%IP%:5000"

endlocal
