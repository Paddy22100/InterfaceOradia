# server.py
import os
import pathlib
import re

from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# ── 1) Chargement des variables depuis .env ────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN") or ""

# Si on est en production Railway, afficher un message pour debug
if os.getenv("RAILWAY_STATIC_URL"):
    print("✅ Variables injectées depuis Railway")
else:
    print("⚠️  Attention : Variables d'environnement chargées depuis .env")

# ── 2) Vérifier la présence des variables importantes ──────────────────────
if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY manquant ! Le serveur démarre mais l'API IA ne fonctionnera pas.")
if not VERCEL_TOKEN:
    print("⚠️ VERCEL_TOKEN manquant (optionnel)")

# ── 3) Client OpenAI ────────────────────────────────────────────────────────
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ── 4) Création de l’app FastAPI ────────────────────────────────────────────
app = FastAPI(
    title="Oradia Backend API",
    description="API pour générer et servir des pages HTML",
    version="1.0"
)

# ── 5) Serveur de fichiers statiques ────────────────────────────────────────
static_dir = pathlib.Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ── 6) Route pour la page d’accueil ─────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    index_file = pathlib.Path("index.html")
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse(
        "<h1>Bienvenue sur Oradia Backend 🚀</h1>"
        "<p>Ajoutez un fichier <code>index.html</code> dans le dossier racine pour le servir.</p>"
    )

# ── 7) Route de test : /hello ───────────────────────────────────────────────
@app.get("/hello")
async def hello():
    return {"message": "Bonjour Aurélia 🌸"}

# ── 8) Génération d’une page HTML via l’IA ──────────────────────────────────
@app.post("/api/generate-page")
async def generate_page(request: Request):
    if not client:
        return JSONResponse(content={"error": "OPENAI_API_KEY non configuré"}, status_code=500)
    try:
        data = await request.json()
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return JSONResponse(content={"error": "Prompt manquant"}, status_code=400)

        # Extraire un nom de page dynamique
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
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=800
        )
        html_content = resp.choices[0].message.content.strip()

        # Enregistrer le HTML dans un fichier
        filename = f"{page_name}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        return {
            "filename": filename,
            "message": f"✅ Page '{filename}' créée avec succès"
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ── 9) Lancement avec Uvicorn pour Railway ─────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Railway définit $PORT automatiquement
    print(f"▶▶▶ Oradia backend lancé sur http://0.0.0.0:{port} ◀◀◀")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
