@echo off
setlocal
cd /d %~dp0
call venv\Scripts\activate

echo == Python ==
python --version

echo == Pip packages (skracen prikaz) ==
pip show waitress | findstr /i "Version"
pip show watchdog | findstr /i "Version"
pip show flask    | findstr /i "Version"

echo == Pokrecem waitress (production) ==
waitress-serve --host=0.0.0.0 --port=5000 --call gallery_app:create_app

echo.
echo (Ako je doslo do greske, ostavljam prozor otvoren.)
pause
