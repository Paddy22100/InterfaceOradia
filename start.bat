@echo off
title Oradia - Lancement de l'Agent IA
echo ================================================================
echo               Oradia - Lancement de l'Agent IA
echo ================================================================
echo.
echo 1. Mode Debug (console visible)
echo 2. Mode Silencieux (aucune sortie)
echo.
echo Démarrage automatique en mode silencieux dans 5 secondes...
set /p mode=Choix (1/2) : <nul
timeout /t 5 >nul
if not defined mode set mode=2

if "%mode%"=="1" (
    echo.
    echo -> Lancement en mode debug...
    echo ------------------------------
    venv\Scripts\python.exe server.py
) else (
    echo.
    echo -> Lancement en mode silencieux...
    echo ------------------------------
    start /min "" venv\Scripts\python.exe server.py >nul 2>&1

    echo En attente du démarrage du serveur...
    set server_ready=0
    for /L %%i in (1,1,10) do (
        timeout /t 1 >nul
        powershell -Command ^
        "$r = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000; ^
         if ($r.TcpTestSucceeded) { exit 0 } else { exit 1 }"
        if %errorlevel%==0 (
            set server_ready=1
            goto server_up
        )
    )
    echo Erreur : le serveur n'a pas démarré.
    exit /b

    :server_up
    echo Le serveur est prêt. Ouverture du navigateur...
    start "" http://127.0.0.1:8000
)
