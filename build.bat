@echo off
echo ===============================================
echo   🚀 Build de InterfaceOradia.exe en cours...
echo ===============================================

REM Activation de l'environnement virtuel
call venv\Scripts\activate

REM Construction avec PyInstaller
pyinstaller --console --onefile --icon=logo.ico ^
--name InterfaceOradia ^
--add-data "index.html;." ^
--add-data "styles.css;." ^
--add-data "main.js;." ^
--add-data ".env;." ^
--add-data "static;static" ^
--add-data "python_embedded;python_embedded" ^
--add-data "server.py;." ^
launcher.py

echo ===============================================
echo ✅ Build terminé. Vérifie le dossier dist\
echo ===============================================
pause
