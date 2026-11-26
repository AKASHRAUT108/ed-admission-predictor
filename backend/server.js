const express = require("express");
const cors = require("cors");
const { predictWithPython } = require("./pythonBridge");

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Health check
app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    service: "ED Admission Predictor API",
    timestamp: new Date().toISOString(),
  });
});

// Prediction endpoint using the real Python model
app.post("/api/predict", async (req, res) => {
  const payload = req.body;

  // Basic validation
  if (
    payload.age === undefined ||
    payload.triage_level === undefined ||
    payload.chief_complaint === undefined
  ) {
    return res.status(400).json({
      error: "Missing required fields: age, triage_level, chief_complaint",
    });
  }

  try {
    const result = await predictWithPython(payload);
    res.json(result);
  } catch (err) {
    console.error("Prediction error:", err.message);
    res.status(500).json({
      error: "Prediction failed",
      detail: err.message,
    });
  }
});

app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/api/health`);
});