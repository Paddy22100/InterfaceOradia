@echo off
cd /d "%~dp0"
title Oradia - Agent IA (Mode Silencieux)

REM Lancer le serveur Python sans logs
start "" /min venv\Scripts\python.exe server.py --no-access-log --log-level critical

REM Vérifier que le serveur est prêt
echo Attente du démarrage du serveur...
set server_ready=0
for /L %%i in (1,1,15) do (
    timeout /t 1 >nul
    powershell -Command ^
    "$r = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000; ^
     if ($r.TcpTestSucceeded) { exit 0 } else { exit 1 }"
    if %errorlevel%==0 (
        set server_ready=1
        goto server_up
    )
)

echo ❌ Le serveur n'a pas démarré.
exit /b

:server_up
start "" http://127.0.0.1:8000
exit
