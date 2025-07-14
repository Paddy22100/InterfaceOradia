# server.py
import os
import pathlib
import re

from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
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
app = FastAPI()

# ── 4) Route pour la page d’accueil ─────────────────────────────────────────
@app.get("/")
async def index():
    index_path = pathlib.Path("index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse(content={"error": "index.html non trouvé"}, status_code=404)

# ── 5) Route de test : /hello ───────────────────────────────────────────────
@app.get("/hello")
async def hello():
    return {"message": "Bonjour Aurélia 🌸"}

# ── 6) Génération d’une page HTML via l’IA ──────────────────────────────────
@app.post("/api/generate-page")
async def generate_page(request: Request):
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
            {"role": "system", "content": system
