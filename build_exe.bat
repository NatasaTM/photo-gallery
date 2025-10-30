@echo off
setlocal
cd /d %~dp0

REM Aktiviraj venv ili ga kreiraj ako ne postoji
if not exist venv (
  echo [setup] Kreiram venv...
  python -m venv venv || (echo GRESKA: Python nije u PATH-u & pause & exit /b 1)
)
call venv\Scripts\activate

REM Instaliraj pyinstaller ako treba
python -c "import PyInstaller" 2>nul || pip install pyinstaller

echo [build] Pravim EXE...
pyinstaller --onefile --name FotoGalerija ^
  --hidden-import=watchdog.observers.winapi ^
  --hidden-import=watchdog.observers.read_directory_changes ^
  run_prod.py

echo.
echo ✅ EXE gotov: dist\FotoGalerija.exe
pause
