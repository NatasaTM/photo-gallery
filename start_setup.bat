@echo off
setlocal
REM Podesi apsolutnu putanju projekta ako pokrećeš iz prečice
cd /d %~dp0

echo [1/3] Kreiram venv...
python -m venv venv
if errorlevel 1 (
  echo GRESKA: Nije uspelo kreiranje venv-a. Proveri da li je Python u PATH-u.
  pause
  exit /b 1
)

echo [2/3] Aktiviram venv...
call venv\Scripts\activate

echo [3/3] Instaliram pakete...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Setup gotov!
echo - Pokreni DEV:   start_dev.bat
echo - Pokreni PROD:  start_prod.bat
pause
