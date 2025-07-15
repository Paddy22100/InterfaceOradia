# agent.py
import os
import pathlib
import openai
from git import Repo
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ── Charger les variables d'environnement ──────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_PATH = pathlib.Path(__file__).parent  # Chemin du projet InterfaceOradia

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY manquant dans les variables d'environnement")
if not GITHUB_TOKEN:
    raise RuntimeError("❌ GITHUB_TOKEN manquant dans les variables d'environnement")

# Configurer OpenAI
openai.api_key = OPENAI_API_KEY

# ── L’agent qui modifie le frontend ─────────────────────────────────────
def process_user_instruction(prompt: str):
    """Utiliser l’IA pour modifier ou créer une page"""
    print("🤖 Traitement de la consigne :", prompt)

    # Appel OpenAI pour générer le nouveau code HTML
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu es un assistant qui modifie le frontend HTML/CSS/JS du projet InterfaceOradia selon la consigne donnée."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    html_code = response.choices[0].message.content.strip()

    # Écriture dans un fichier HTML (pour l'exemple on écrase index.html)
    file_path = REPO_PATH / "index.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    print("✅ Modifications écrites dans index.html")

    # Commit & push sur GitHub
    commit_and_push(f"💡 Modifications IA : {prompt}")

def commit_and_push(message: str):
    """Effectuer un commit et pousser sur GitHub"""
    print("📦 Commit & Push...")
    repo = Repo(REPO_PATH)
    repo.git.add(all=True)
    repo.index.commit(message)
    repo.git.push(f"https://{GITHUB_TOKEN}@github.com/Paddy22100/InterfaceOradia.git", "main")
    print("✅ Changements poussés sur GitHub")

# ── Backend FastAPI pour piloter l’agent ───────────────────────────────
app = FastAPI()

@app.post("/agent")
async def call_agent(request: Request):
    """API pour envoyer une consigne à l’agent"""
    data = await request.json()
    instruction = data.get("instruction", "")
    if not instruction:
        return JSONResponse(content={"error": "❌ Instruction manquante"}, status_code=400)

    try:
        process_user_instruction(instruction)
        return {"status": "success", "message": "✅ Modification appliquée et poussée"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
