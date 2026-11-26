"""
Generate synthetic Emergency Department visit data.

The goal is to create a dataset that is structurally realistic:
- Features reflect what a triage nurse records at intake.
- The target (admitted) is generated from a latent risk function,
  so the model has a real signal to learn.

Output: data/ed_visits.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Reproducibility
np.random.seed(42)
N = 5000  # number of ED visits

# ------------------------------------------------------------------
# 1. Basic demographic and arrival features
# ------------------------------------------------------------------
age = np.random.randint(1, 95, N)

# Triage level: 1 (most urgent) to 5 (least urgent)
# Distribution roughly follows real ED triage patterns
triage_level = np.random.choice(
    [1, 2, 3, 4, 5],
    N,
    p=[0.05, 0.15, 0.40, 0.30, 0.10]
)

# Arrival hour: 0-23, with peaks in late morning and evening
hour_weights = np.array([
    1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 7,
    6, 5, 5, 5, 6, 7, 8, 8, 7, 6, 4, 2
], dtype=float)
hour_weights = hour_weights / hour_weights.sum()
arrival_hour = np.random.choice(range(24), N, p=hour_weights)

# Chief complaint category
complaints = [
    "chest_pain", "abdominal_pain", "dyspnea",
    "fever", "injury", "neuro", "other"
]
complaint_probs = [0.10, 0.15, 0.12, 0.18, 0.20, 0.10, 0.15]
chief_complaint = np.random.choice(complaints, N, p=complaint_probs)

# ------------------------------------------------------------------
# 2. Vital signs (proxies)
# ------------------------------------------------------------------
systolic_bp = np.random.normal(125, 20, N).clip(70, 220)
heart_rate = np.random.normal(85, 18, N).clip(40, 180)
temperature = np.random.normal(37.0, 0.8, N).clip(35.0, 41.0)
spo2 = np.random.normal(96, 3, N).clip(70, 100)

# ------------------------------------------------------------------
# 3. Generate target: admitted (0/1)
# ------------------------------------------------------------------
# Latent risk score: higher score => more likely to be admitted
risk = (
    -3.0
    + 0.03 * age
    + 0.60 * (6 - triage_level)                 # lower triage number => higher risk
    + 0.80 * (chief_complaint == "chest_pain")
    + 0.70 * (chief_complaint == "dyspnea")
    + 0.50 * (chief_complaint == "neuro")
    + 0.02 * np.where(systolic_bp < 100, 100 - systolic_bp, 0)
    + 0.015 * np.where(heart_rate > 110, heart_rate - 110, 0)
    + 1.50 * (temperature > 38.5)
    + 1.20 * (spo2 < 92)
)

prob_admitted = 1 / (1 + np.exp(-risk))
admitted = np.random.binomial(1, prob_admitted)

# ------------------------------------------------------------------
# 4. Assemble DataFrame
# ------------------------------------------------------------------
df = pd.DataFrame({
    "age": age,
    "triage_level": triage_level,
    "arrival_hour": arrival_hour,
    "chief_complaint": chief_complaint,
    "systolic_bp": systolic_bp.round(1),
    "heart_rate": heart_rate.round(1),
    "temperature": temperature.round(2),
    "spo2": spo2.round(1),
    "admitted": admitted,
})

# ------------------------------------------------------------------
# 5. Save
# ------------------------------------------------------------------
output_path = Path(__file__).resolve().parent.parent / "data" / "ed_visits.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

print(f"Generated {len(df)} records")
print(f"Admission rate: {df['admitted'].mean():.3f}")
print(f"Saved to: {output_path}")
print("\nFirst 5 rows:")
print(df.head())