"""
Train a baseline model to predict ED admission.

Steps:
1. Load data/ed_visits.csv
2. Encode categorical features (chief_complaint)
3. Split into train/test
4. Train Logistic Regression and XGBoost
5. Evaluate and compare
6. Save the best model to ml/model.pkl
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    confusion_matrix,
    classification_report,
)
from xgboost import XGBClassifier

# ------------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------------
data_path = Path(__file__).resolve().parent.parent / "data" / "ed_visits.csv"
df = pd.read_csv(data_path)

print(f"Loaded {len(df)} records")
print(f"Admission rate: {df['admitted'].mean():.3f}")

# ------------------------------------------------------------------
# 2. Define features and target
# ------------------------------------------------------------------
target = "admitted"

categorical_features = ["chief_complaint"]
numeric_features = [
    "age",
    "triage_level",
    "arrival_hour",
    "systolic_bp",
    "heart_rate",
    "temperature",
    "spo2",
]

X = df[categorical_features + numeric_features]
y = df[target]

# ------------------------------------------------------------------
# 3. Preprocessing pipeline
# ------------------------------------------------------------------
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("num", StandardScaler(), numeric_features),
    ]
)

# ------------------------------------------------------------------
# 4. Train/test split
# ------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTrain size: {len(X_train)}")
print(f"Test size:  {len(X_test)}")

# ------------------------------------------------------------------
# 5. Train Logistic Regression baseline
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("Logistic Regression")
print("=" * 60)

lr_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
])

lr_pipeline.fit(X_train, y_train)

y_pred_lr = lr_pipeline.predict(X_test)
y_prob_lr = lr_pipeline.predict_proba(X_test)[:, 1]

print(f"ROC-AUC:  {roc_auc_score(y_test, y_prob_lr):.4f}")
print(f"Accuracy: {accuracy_score(y_test, y_pred_lr):.4f}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred_lr))
print("\nClassification Report:")
print(classification_report(y_test, y_pred_lr))

# ------------------------------------------------------------------
# 6. Train XGBoost
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("XGBoost")
print("=" * 60)

xgb_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss",
    )),
])

xgb_pipeline.fit(X_train, y_train)

y_pred_xgb = xgb_pipeline.predict(X_test)
y_prob_xgb = xgb_pipeline.predict_proba(X_test)[:, 1]

print(f"ROC-AUC:  {roc_auc_score(y_test, y_prob_xgb):.4f}")
print(f"Accuracy: {accuracy_score(y_test, y_pred_xgb):.4f}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred_xgb))
print("\nClassification Report:")
print(classification_report(y_test, y_pred_xgb))

# ------------------------------------------------------------------
# 7. Save the best model
# ------------------------------------------------------------------
# For simplicity, choose XGBoost if its ROC-AUC is higher,
# otherwise Logistic Regression.
lr_auc = roc_auc_score(y_test, y_prob_lr)
xgb_auc = roc_auc_score(y_test, y_prob_xgb)

if xgb_auc >= lr_auc:
    best_model = xgb_pipeline
    best_name = "XGBoost"
    best_auc = xgb_auc
else:
    best_model = lr_pipeline
    best_name = "Logistic Regression"
    best_auc = lr_auc

model_path = Path(__file__).resolve().parent / "model.pkl"
joblib.dump(best_model, model_path)

print("\n" + "=" * 60)
print(f"Best model: {best_name} (ROC-AUC: {best_auc:.4f})")
print(f"Saved to: {model_path}")
print("=" * 60)