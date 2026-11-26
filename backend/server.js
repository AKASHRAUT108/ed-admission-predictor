const express = require("express");
const cors = require("cors");

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// ------------------------------------------------------------------
// Health check endpoint
// ------------------------------------------------------------------
app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    service: "ED Admission Predictor API",
    timestamp: new Date().toISOString(),
  });
});

// ------------------------------------------------------------------
// Prediction endpoint (placeholder — real model will be wired in later)
// ------------------------------------------------------------------
app.post("/api/predict", (req, res) => {
  const {
    age,
    triage_level,
    arrival_hour,
    chief_complaint,
    systolic_bp,
    heart_rate,
    temperature,
    spo2,
  } = req.body;

  // Basic validation
  if (
    age === undefined ||
    triage_level === undefined ||
    chief_complaint === undefined
  ) {
    return res.status(400).json({
      error: "Missing required fields: age, triage_level, chief_complaint",
    });
  }

  // Placeholder prediction logic (will be replaced by real model)
  // Simple heuristic: higher risk for older patients and lower triage levels
  let riskScore = 0.3;
  if (age > 60) riskScore += 0.2;
  if (triage_level <= 2) riskScore += 0.3;
  if (chief_complaint === "chest_pain") riskScore += 0.15;
  if (spo2 !== undefined && spo2 < 92) riskScore += 0.2;

  riskScore = Math.min(riskScore, 0.99);

  res.json({
    admission_probability: parseFloat(riskScore.toFixed(4)),
    recommendation:
      riskScore > 0.6
        ? "High risk — reserve bed in advance"
        : riskScore > 0.4
        ? "Moderate risk — monitor closely"
        : "Low risk — standard triage",
    model_version: "placeholder-v1",
  });
});

// ------------------------------------------------------------------
// Start server
// ------------------------------------------------------------------
app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/api/health`);
});