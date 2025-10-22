@echo off
setlocal
cd /d %~dp0
call venv\Scripts\activate
REM Pokrece WSGI server (Waitress) na portu 5000
waitress-serve --host=0.0.0.0 --port=5000 --call gallery_app:create_app
