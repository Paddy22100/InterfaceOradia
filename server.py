# server.py
import os
import pathlib
import re
import sys

from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# ── 1) Chargement des variables depuis .env ────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN") or ""

# Vérification des variables d’environnement
if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY manquant ! L'API IA ne fonctionnera pas.")
else:
    print("✅ OPENAI_API_KEY détecté.")

# ── 2) Client OpenAI ───────────────────────────────────────────────────────
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ── 3) Création de l’app FastAPI ──────────────────────────────────────────
app = FastAPI(
    title="Oradia Backend API",
    description="API pour générer et servir des pages HTML",
    version="1.3"
)

# ── 4) Serveur de fichiers statiques ──────────────────────────────────────
static_dir = pathlib.Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print("⚠️ Dossier /static manquant, les fichiers statiques ne seront pas servis.")

# ── 5) Route favicon (logo.ico) ───────────────────────────────────────────
@app.get("/favicon.ico")
async def favicon():
    favicon_file = pathlib.Path(__file__).parent / "logo.ico"
    if favicon_file.exists():
        return FileResponse(favicon_file)
    raise HTTPException(status_code=404, detail="Favicon non trouvé")

# ── 6) Route pour la page d’accueil ───────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    index_file = pathlib.Path(__file__).parent / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse(
        "<h1>Bienvenue sur Oradia Backend 🚀</h1>"
        "<p>Ajoutez un fichier <code>index.html</code> dans le dossier racine.</p>"
    )

# ── 7) Route pour servir les fichiers HTML générés ─────────────────────────
@app.get("/{page_name}.html", response_class=HTMLResponse)
async def serve_generated_page(page_name: str):
    file_path = pathlib.Path(__file__).parent / f"{page_name}.html"
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page non trouvée")

# ── 8) Génération d’une page HTML via l’IA ────────────────────────────────
@app.post("/api/generate-page")
async def generate_page(request: Request):
    if not client:
        return JSONResponse(content={"error": "OPENAI_API_KEY non configuré"}, status_code=500)
    try:
        data = await request.json()
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return JSONResponse(content={"error": "Prompt manquant"}, status_code=400)

        # Extraction d’un nom de page à partir du prompt
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

        # Sauvegarde de la page HTML générée
        filename = pathlib.Path(__file__).parent / f"{page_name}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        return {
            "filename": str(filename),
            "message": f"✅ Page '{filename.name}' créée avec succès"
        }

    except Exception as e:
        print(f"❌ Erreur lors de la génération de page : {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ── 9) Lancement avec Uvicorn ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    print(f"▶▶▶ Oradia backend lancé sur http://0.0.0.0:{port} ◀◀◀")
    print("✅ Serveur bien démarré")

    try:
        uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
    except Exception as e:
        print(f"❌ Erreur de lancement : {e}")
        input("🔴 Appuyez sur Entrée pour fermer...")
