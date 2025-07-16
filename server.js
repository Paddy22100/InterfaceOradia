const express = require("express");
const app = express();

const PORT = process.env.PORT || 3000;

// Test route
app.get("/", (req, res) => {
  res.send("✅ Backend Oradia is running.");
});

// API route
app.post("/api/generate-page", (req, res) => {
  res.json({ message: "🎉 Page générée depuis le backend Oradia !" });
});

app.listen(PORT, () => {
  console.log(`🚀 Backend running on port ${PORT}`);
});
