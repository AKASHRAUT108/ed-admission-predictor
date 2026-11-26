"""
Prediction script called by the Node.js backend.

Reads a JSON object from stdin containing patient features.
Loads the trained model from model.pkl.
Writes a JSON object to stdout with the prediction result.

Input JSON schema:
{
    "age": int,
    "triage_level": int,
    "arrival_hour": int,
    "chief_complaint": str,
    "systolic_bp": float,
    "heart_rate": float,
    "temperature": float,
    "spo2": float
}

Output JSON schema:
{
    "admission_probability": float,
    "recommendation": str,
    "model_version": str
}
"""

import sys
import json
import joblib
import pandas as pd
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"

CATEGORICAL_FEATURES = ["chief_complaint"]
NUMERIC_FEATURES = [
    "age",
    "triage_level",
    "arrival_hour",
    "systolic_bp",
    "heart_rate",
    "temperature",
    "spo2",
]


def build_recommendation(prob: float) -> str:
    if prob >= 0.65:
        return "High risk — reserve bed in advance"
    elif prob >= 0.40:
        return "Moderate risk — monitor closely"
    else:
        return "Low risk — standard triage"


def main():
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input)
    except Exception as e:
        print(json.dumps({"error": f"Invalid input JSON: {str(e)}"}))
        sys.exit(1)

    # Validate required fields
    required = ["age", "triage_level", "chief_complaint"]
    for field in required:
        if field not in payload:
            print(json.dumps({"error": f"Missing required field: {field}"}))
            sys.exit(1)

    # Fill optional fields with sensible defaults if missing
    defaults = {
        "arrival_hour": 12,
        "systolic_bp": 120.0,
        "heart_rate": 80.0,
        "temperature": 37.0,
        "spo2": 97.0,
    }
    for field, default in defaults.items():
        if field not in payload or payload[field] is None:
            payload[field] = default

    # Build a single-row DataFrame with the exact feature order used in training
    row = {feat: payload[feat] for feat in CATEGORICAL_FEATURES + NUMERIC_FEATURES}
    X = pd.DataFrame([row])

    # Load model and predict
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(json.dumps({"error": f"Failed to load model: {str(e)}"}))
        sys.exit(1)

    try:
        prob = float(model.predict_proba(X)[0, 1])
    except Exception as e:
        print(json.dumps({"error": f"Prediction failed: {str(e)}"}))
        sys.exit(1)

    result = {
        "admission_probability": round(prob, 4),
        "recommendation": build_recommendation(prob),
        "model_version": "logreg-v1",
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()