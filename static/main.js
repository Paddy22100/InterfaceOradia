// main.js

// Sélecteurs
const btnGenerate = document.getElementById("btn-generate");
const inputPrompt = document.getElementById("promptInput");
const previewDiv  = document.getElementById("preview");
const spinnerCont = document.getElementById("spinner-container");
const btnDeploy   = document.getElementById("btn-deploy");

let lastFilename = null;

// ───> RESET DU CHAMP À CHAQUE CHARGEMENT
inputPrompt.value = "";

// Fonction de génération (extrait pour pouvoir la ré-utiliser)
async function generatePage() {
  const prompt = inputPrompt.value.trim();
  if (!prompt) return alert("Il faut un prompt.");

  // Reset UI
  previewDiv.innerHTML      = "";
  spinnerCont.style.display = "block";
  btnDeploy.style.display   = "none";
  lastFilename = null;

  try {
    const res = await fetch("/api/generate-page", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ prompt })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || res.statusText);

    lastFilename = data.filename;
    previewDiv.innerHTML = `
      <h3>Aperçu de <code>${lastFilename}</code></h3>
      <iframe src="/${lastFilename}"></iframe>
    `;
    btnDeploy.style.display = "inline-block";

  } catch (err) {
    previewDiv.innerHTML = `<p>❌ Erreur de génération : ${err.message}</p>`;
  } finally {
    spinnerCont.style.display = "none";
  }
}

// Clic sur le bouton
btnGenerate.addEventListener("click", generatePage);

// **Nouvelle partie : Entrée clavier**
inputPrompt.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();    // empêche le « ding » par défaut  
    generatePage();
  }
});

// Déploiement
btnDeploy.addEventListener("click", async () => {
  if (!lastFilename) return;
  btnDeploy.disabled  = true;
  btnDeploy.innerText = "⏳ Déploiement…";

  try {
    const res  = await fetch("/api/deploy", { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || res.statusText);
    window.open(data.url, "_blank");
  } catch (err) {
    alert("Échec déploiement : " + err.message);
  } finally {
    btnDeploy.disabled  = false;
    btnDeploy.innerText = "🚀 Déployer sur Vercel";
  }
});
