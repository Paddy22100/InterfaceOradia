import subprocess
import sys
import os
import webbrowser
import time
import socket

def resource_path(relative_path):
    """Retourne le chemin absolu pour PyInstaller ou exécution normale."""
    try:
        base_path = sys._MEIPASS  # Dossier temporaire PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def start_server():
    """Lance le serveur FastAPI en arrière-plan."""
    python_exe = resource_path("python_embedded/python.exe")
    server_script = resource_path("server.py")

    print(f"🔍 Python embarqué : {python_exe}")
    print(f"🔍 Script serveur  : {server_script}")

    if not os.path.exists(python_exe):
        print(f"❌ Python embarqué introuvable : {python_exe}")
        return False
    if not os.path.exists(server_script):
        print(f"❌ Fichier server.py introuvable : {server_script}")
        return False

    print("🚀 Lancement du serveur...")
    try:
        # Ne pas rediriger la sortie pour voir les erreurs dans la console
        subprocess.Popen(
            [python_exe, server_script],
            cwd=os.path.dirname(server_script)
        )
        print("✅ Serveur lancé (en arrière-plan).")
        time.sleep(2)  # Donne un peu de temps pour démarrer
        return True
    except Exception as e:
        print(f"❌ Erreur au démarrage du serveur : {e}")
        return False

def wait_for_server(host="127.0.0.1", port=8000, timeout=60):
    """Attend que le serveur FastAPI soit prêt."""
    print(f"⏳ Attente du serveur sur http://{host}:{port} ...")
    for i in range(timeout):
        try:
            with socket.create_connection((host, port), timeout=1):
                print(f"✅ Serveur détecté après {i + 1} secondes.")
                return True
        except OSError:
            time.sleep(1)
            print(f"⏳ Tentative {i+1}/{timeout}...")
    print(f"❌ Le serveur ne répond pas après {timeout} secondes.")
    return False

def open_browser():
    """Ouvre le navigateur."""
    print("🌐 Ouverture du navigateur...")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("🎯 Lancement InterfaceOradia.exe")
    if start_server():
        if wait_for_server():
            open_browser()
        else:
            print("⚠️ Échec : le serveur n'a pas démarré à temps.")
            print("📄 Vérifie la console ci-dessus pour voir les erreurs du serveur.")
    else:
        print("⚠️ Impossible de démarrer le serveur.")
    input("\n🔴 Appuyez sur Entrée pour quitter...")
 