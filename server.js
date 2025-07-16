const express = require("express");
const cors = require("cors"); // ✅ Autoriser toutes origines
const app = express();

const PORT = process.env.PORT || 3000;

// ✅ Autoriser toutes les origines avec CORS large
app.use(cors({
  origin: "*", // ✅ Autoriser toutes les origines
  methods: ["GET", "POST", "OPTIONS"], // ✅ Autoriser les méthodes courantes
  allowedHeaders: ["Content-Type"], // ✅ Autoriser les headers nécessaires
}));

// ✅ Gérer les requêtes pré-vol (OPTIONS) pour toutes les routes
app.options("*", cors());

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
