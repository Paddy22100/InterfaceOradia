const express = require("express");
const cors = require("cors"); // ✅ Autoriser toutes origines
const app = express();

const PORT = process.env.PORT || 3000;

// ✅ Middleware CORS ultra-large : autoriser toutes origines, méthodes et headers
app.use(cors({
  origin: "*", // ✅ Autoriser toutes les origines
  methods: ["GET", "POST", "OPTIONS", "PUT", "DELETE"], // ✅ Méthodes HTTP complètes
  allowedHeaders: ["Content-Type", "Authorization", "X-Requested-With"], // ✅ Headers acceptés
  credentials: true // ✅ Autoriser les cookies (si besoin plus tard)
}));

// ✅ Ajouter manuellement les en-têtes CORS pour être sûr
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE");
  res.header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With");
  if (req.method === "OPTIONS") {
    return res.sendStatus(204); // ✅ Répondre aux pré-vols OPTIONS
  }
  next();
});

// ✅ Middleware pour parser le JSON
app.use(express.json());

// ✅ Logger toutes les requêtes
app.use((req, res, next) => {
  console.log(`📥 ${req.method} ${req.url}`);
  next();
});

// ✅ Test route GET
app.get("/", (req, res) => {
  res.send("✅ Backend Oradia is running.");
});

// ✅ API route POST
app.post("/api/generate-page", (req, res) => {
  const { prompt } = req.body || {};
  console.log(`📩 Prompt reçu : ${prompt}`);
  if (!prompt) {
    return res.status(400).json({ message: "❌ Aucun prompt fourni" });
  }
  res.json({ message: `🎉 Page générée pour le prompt : "${prompt}"` });
});

// ✅ Catch-all pour routes inconnues
app.use((req, res) => {
  res.status(404).json({ message: "❌ Route non trouvée" });
});

// ✅ Démarrage du serveur
app.listen(PORT, () => {
  console.log(`🚀 Backend Oradia running on port ${PORT}`);
});
