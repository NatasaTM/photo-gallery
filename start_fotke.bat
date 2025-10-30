@echo off
setlocal
cd /d %~dp0

echo Pokrecem FotoGaleriju...
start "" "%~dp0FotoGalerija.exe"

REM sacekaj malo da server krene
timeout /t 3 >nul

REM === pronadji PRAVU LAN IPv4 adresu (prefer 192.168.*, pa 10.*, pa 172.16-31.*) ===
set "IP="

REM 1) 192.168.*
for /f "tokens=2 delims=:" %%A in ('
  ipconfig ^| findstr /R /C:"IPv4 Address" ^| findstr /C:"192.168."
') do set "IP=%%A"

REM 2) 10.*
if not defined IP (
  for /f "tokens=2 delims=:" %%A in ('
    ipconfig ^| findstr /R /C:"IPv4 Address" ^| findstr /C:" 10."
  ') do set "IP=%%A"
)

REM 3) 172.16-31.*
if not defined IP (
  for /f "tokens=2 delims=:" %%A in ('
    ipconfig ^| findstr /R /C:"IPv4 Address" ^| findstr /R "172\.1[6-9]\.|172\.2[0-9]\.|172\.3[01]\."
  ') do set "IP=%%A"
)

REM ocisti razmake
set "IP=%IP: =%"

echo.
echo ========================================
echo  Lokalno (ovo se vec otvorilo):
echo      http://localhost:5000
echo.
echo  Za tablete/telefone u LAN-u:
if defined IP (
  echo      http://%IP%:5000
) else (
  echo      (Nije nadjena LAN adresa - proveri mrezu)
)
echo ========================================
echo.

REM otvori SAMO lokalnu adresu na laptopu
REM (ovo sada radi automatski iz gallery_app.py)
REM start "" "http://localhost:5000"

REM opciono: kopiraj LAN URL u clipboard (radi na Win10/11)
REM ako ne zelis copy u clipboard, obrisi sledecu liniju
if defined IP powershell -NoProfile -Command "Set-Clipboard 'http://%IP%:5000'"

echo.
echo The app is running in the background until you run stop_fotke.bat.
echo.
pause
exit

endlocal
