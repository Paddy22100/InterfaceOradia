const express = require("express");
const cors = require("cors"); // ✅ Permet les appels depuis le frontend
const app = express();

const PORT = process.env.PORT || 3000;

// ✅ Middleware pour parser le JSON
app.use(express.json());

// ✅ Autoriser toutes les origines (utile pour le frontend)
app.use(cors());

// ✅ Test route
app.get("/", (req, res) => {
  res.send("✅ Backend Oradia is running.");
});

// ✅ API route
app.post("/api/generate-page", (req, res) => {
  const { prompt } = req.body || {};
  console.log(`📩 Prompt reçu : ${prompt}`);
  res.json({ message: `🎉 Page générée pour le prompt : "${prompt}"` });
});

// ✅ Démarrage du serveur
app.listen(PORT, () => {
  console.log(`🚀 Backend Oradia running on port ${PORT}`);
});
