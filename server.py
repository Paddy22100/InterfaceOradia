# server.py
import os
import pathlib
import subprocess
import re

from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory

# ── 1) Chargement des variables depuis .env ────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERCEL_TOKEN   = os.getenv("VERCEL_TOKEN")

if not OPENAI_API_KEY:
    raise RuntimeError("🔴 Définis OPENAI_API_KEY dans ton fichier .env")
if not VERCEL_TOKEN:
    raise RuntimeError("🔴 Définis VERCEL_TOKEN dans ton fichier .env")

# ── 2) Client OpenAI ────────────────────────────────────────────────────────
client = OpenAI(api_key=OPENAI_API_KEY)

# ── 3) Création de l’app Flask ──────────────────────────────────────────────
app = Flask(
    __name__,
    static_folder=".",      # on sert tout le dossier courant en statique
    static_url_path=""      # aux URLs racine ("/styles.css", "/main.js", etc.)
)

# ── 4) Route pour la page d’accueil ─────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return send_from_directory(".", "index.html")

# ── 5) Génération d’une page HTML via l’IA ─────────────────────────────────
@app.route("/api/generate-page", methods=["POST"])
def generate_page():
    data   = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify(error="Prompt manquant"), 400

    # Extraire un nom de page dynamique (ex : "page test" → test.html)
    m = re.search(r"page\s+(?:de|d['’])?\s*([A-Za-z0-9_-]+)", prompt, re.IGNORECASE)
    page_name = (m.group(1).lower() if m else "page")

    system_msg = (
        f"Tu es un assistant qui crée une page HTML complète nommée '{page_name}.html' "
        "pour le site oradia.fr. Renvoie uniquement le code HTML final."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.8,
        max_tokens=800
    )
    html = resp.choices[0].message.content.strip()

    # Enregistrer le HTML dans un fichier
    filename = f"{page_name}.html"
    with open(pathlib.Path(filename), "w", encoding="utf-8") as f:
        f.write(html)

    return jsonify(filename=filename)

# ── 6) Déploiement automatique sur Vercel ──────────────────────────────────
@app.route("/api/deploy", methods=["POST"])
def deploy():
    try:
        # On appelle vercel.cmd directement, avec --yes pour confirmer
        cmd = f"vercel.cmd --prod --token {VERCEL_TOKEN} --yes"
        print("🔧 Lancement de :", cmd)
        out = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )
        print("✅ Vercel a répondu :", out)
        # On suppose que la dernière ligne du stdout est l'URL de prod
        url = out.strip().split("\n")[-1]
    except subprocess.CalledProcessError as e:
        print("❌ Erreur Vercel :", e.output)
        return jsonify(error=f"❌ Erreur Vercel : {e.output}"), 500
    except FileNotFoundError as e:
        print("❌ CLI introuvable :", e)
        return jsonify(error="❌ Erreur interne : CLI Vercel introuvable"), 500

    return jsonify(url=url)

# ── 7) Fallback : pour servir toutes les autres pages statiques ────────────
@app.route("/<path:filename>", methods=["GET"])
def serve_static(filename):
    if pathlib.Path(filename).is_file():
        return send_from_directory(".", filename)
    return "Not Found", 404

if __name__ == "__main__":
    # Utilise le port Railway s'il est défini
    port = int(os.environ.get("PORT", 8000))
    print(f"▶▶▶ server.py lancé sur http://0.0.0.0:{port} ◀◀◀")
    app.run(debug=True, host="0.0.0.0", port=port)
