@echo off
echo 🔥 Lancement de l’agent IA Oradia...

REM Étape 1 : Créer l’environnement virtuel s’il n’existe pas déjà
if not exist "venv" (
    echo 📦 Création de l’environnement virtuel...
    python -m venv venv
) else (
    echo ✅ Environnement virtuel déjà présent
)

REM Étape 2 : Activer l’environnement virtuel
echo ⚡ Activation de l’environnement virtuel...
call venv\Scripts\activate

REM Étape 3 : Installer les dépendances
echo 📥 Installation des dépendances (uvicorn, fastapi, gitpython, openai)...
pip install -r requirements.txt || pip install uvicorn fastapi gitpython openai

REM Étape 4 : Lancer le serveur
echo 🚀 Lancement du serveur FastAPI...
uvicorn server:app --reload

pause
