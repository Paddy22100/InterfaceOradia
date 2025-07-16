const express = require("express");
const cors = require("cors"); // ✅ Middleware CORS
const app = express();

const PORT = process.env.PORT || 3000;

// ✅ Middleware CORS ultra-large
app.use(cors({
  origin: "*", // ✅ Autoriser toutes les origines
  methods: ["GET", "POST", "OPTIONS", "PUT", "DELETE"], // ✅ Toutes méthodes HTTP acceptées
  allowedHeaders: ["Content-Type", "Authorization", "X-Requested-With"], // ✅ Headers acceptés
  preflightContinue: false,
  optionsSuccessStatus: 204 // ✅ Répondre 204 pour les pré-vols
}));

// ✅ Middleware pour parser le JSON
app.use(express.json());

// ✅ Logger toutes les requêtes
app.use((req, res, next) => {
  console.log(`📥 ${req.method} ${req.url}`);
  next();
});

// ✅ Route test GET
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
