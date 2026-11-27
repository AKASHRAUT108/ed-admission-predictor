import { useState } from "react";
import "./App.css";

const initialForm = {
  age: 65,
  triage_level: 3,
  arrival_hour: 14,
  chief_complaint: "chest_pain",
  systolic_bp: 130,
  heart_rate: 90,
  temperature: 37.0,
  spo2: 96,
};

const complaints = [
  { value: "chest_pain", label: "Chest Pain" },
  { value: "abdominal_pain", label: "Abdominal Pain" },
  { value: "dyspnea", label: "Dyspnea (Breathing Difficulty)" },
  { value: "fever", label: "Fever" },
  { value: "injury", label: "Injury" },
  { value: "neuro", label: "Neurological" },
  { value: "other", label: "Other" },
];

export default function App() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === "chief_complaint" ? value : Number(value),
    }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    setResult({
      admission_probability: 0.0,
      recommendation: "API call not wired yet (Block 3.2)",
      model_version: "placeholder",
    });
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>ED Admission Predictor</h1>
        <p className="subtitle">
          Predict admission probability and support bed planning
        </p>
      </header>

      <div className="layout">
        <form className="panel form-panel" onSubmit={handleSubmit}>
          <h2>Patient Intake</h2>

          <div className="field">
            <label>Age</label>
            <input
              type="number"
              name="age"
              min="0"
              max="120"
              value={form.age}
              onChange={handleChange}
              required
            />
          </div>

          <div className="field">
            <label>Triage Level (1 = most urgent, 5 = least)</label>
            <select
              name="triage_level"
              value={form.triage_level}
              onChange={handleChange}
            >
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>Arrival Hour (0-23)</label>
            <input
              type="number"
              name="arrival_hour"
              min="0"
              max="23"
              value={form.arrival_hour}
              onChange={handleChange}
            />
          </div>

          <div className="field">
            <label>Chief Complaint</label>
            <select
              name="chief_complaint"
              value={form.chief_complaint}
              onChange={handleChange}
            >
              {complaints.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>

          <div className="field-row">
            <div className="field">
              <label>Systolic BP</label>
              <input
                type="number"
                name="systolic_bp"
                value={form.systolic_bp}
                onChange={handleChange}
              />
            </div>
            <div className="field">
              <label>Heart Rate</label>
              <input
                type="number"
                name="heart_rate"
                value={form.heart_rate}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="field-row">
            <div className="field">
              <label>Temperature (C)</label>
              <input
                type="number"
                step="0.1"
                name="temperature"
                value={form.temperature}
                onChange={handleChange}
              />
            </div>
            <div className="field">
              <label>SpO2 (%)</label>
              <input
                type="number"
                name="spo2"
                value={form.spo2}
                onChange={handleChange}
              />
            </div>
          </div>

          <button type="submit" className="submit-btn">
            Predict Admission
          </button>
        </form>

        <div className="panel result-panel">
          <h2>Prediction Result</h2>

          {result ? (
            <div className="result-content">
              <div className="probability-display">
                <span className="probability-value">
                  {(result.admission_probability * 100).toFixed(1)}%
                </span>
                <span className="probability-label">
                  Admission Probability
                </span>
              </div>
              <div className="recommendation">
                <strong>Recommendation:</strong> {result.recommendation}
              </div>
              <div className="model-version">
                Model: {result.model_version}
              </div>
            </div>
          ) : (
            <p className="empty-state">
              Enter patient details and click Predict to see results.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}