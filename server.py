# server.py
import os
import pathlib
import subprocess
import re

from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ── 1) Chargement des variables depuis .env ────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")

if not OPENAI_API_KEY:
    raise RuntimeError("🔴 Définis OPENAI_API_KEY dans ton fichier .env")
if not VERCEL_TOKEN:
    raise RuntimeError("🔴 Définis VERCEL_TOKEN dans ton fichier .env")

# ── 2) Client OpenAI ────────────────────────────────────────────────────────
client = OpenAI(api_key=OPENAI_API_KEY)

# ── 3) Création de l’app FastAPI ────────────────────────────────────────────
app = FastAPI()

# ── 4) Servir les fichiers statiques (HTML, CSS, JS) ────────────────────────
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# ── 5) Génération d’une page HTML via l’IA ──────────────────────────────────
@app.post("/api/generate-page")
async def generate_page(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt manquant")

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

    return {"filename": filename}

# ── 6) Déploiement automatique sur Vercel ───────────────────────────────────
@app.post("/api/deploy")
async def deploy():
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
        raise HTTPException(status_code=500, detail=f"Erreur Vercel : {e.output}")
    except FileNotFoundError as e:
        print("❌ CLI introuvable :", e)
        raise HTTPException(status_code=500, detail="Erreur interne : CLI Vercel introuvable")

    return {"url": url}

# ── 7) Page d’accueil fallback ──────────────────────────────────────────────
@app.get("/{filename}")
async def serve_static(filename: str):
    file_path = pathlib.Path(filename)
    if file_path.is_file():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Fichier non trouvé")

# ── 8) Lancer l’application ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"▶▶▶ server.py lancé sur http://0.0.0.0:{port} ◀◀◀")
    uvicorn.run(app, host="0.0.0.0", port=port)
