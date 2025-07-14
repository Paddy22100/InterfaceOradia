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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERCEL_TOKEN   = os.getenv("VERCEL_TOKEN")

if not OPENAI_API_KEY:
    raise RuntimeError("🔴 Définis OPENAI_API_KEY dans ton fichier .env")
if not VERCEL_TOKEN:
    raise RuntimeError("🔴 Définis VERCEL_TOKEN dans ton fichier .env")

# ── 2) Client OpenAI ────────────────────────────────────────────────────────
client = OpenAI(api_key=OPENAI_API_KEY)

# ── 3) Création de l’app FastAPI ────────────────────────────────────────────
app = FastAPI(title="Oradia Backend API", description="API pour générer et servir des pages", version="1.0")

# ── 4) Serveur de fichiers statiques ────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── 5) Route pour la page d’accueil ─────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = pathlib.Path("index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>Bienvenue sur Oradia Backend 🚀</h1><p>Ajoute un index.html dans le dossier racine.</p>")

# ── 6) Route de test : /hello ───────────────────────────────────────────────
@app.get("/hello")
async def hello():
    return {"message": "Bonjour Aurélia 🌸"}

# ── 7) Génération d’une page HTML via l’IA ──────────────────────────────────
@app.post("/api/generate-page")
async def generate_page(request: Request):
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
        html = resp.choices[0].message.content.strip()

        # Enregistrer le HTML dans un fichier
        filename = f"{page_name}.html"
        with open(pathlib.Path(filename), "w", encoding="utf-8") as f:
            f.write(html)

        return {"filename": filename, "message": f"Page '{filename}' créée avec succès ✅"}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ── 8) Lancement avec Uvicorn pour Railway ─────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"▶▶▶ Oradia backend lancé sur http://0.0.0.0:{port} ◀◀◀")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
