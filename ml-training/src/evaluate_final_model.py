
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TEST_PATH = (
    PROJECT_ROOT / "ml-training" / "datasets" /
    "splits" / "test.csv"
)

MODEL_PATH = (
    PROJECT_ROOT / "ml-training" / "models" /
    "lightgbm" / "lightgbm_baseline.joblib"
)

OUTPUT_DIR = PROJECT_ROOT / "ml-training" / "models" / "selected"
REPORT_DIR = PROJECT_ROOT / "ml-training" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

SELECTED_THRESHOLD = 0.19899806637425446

print("=" * 65)
print("PHISHGUARD X - FINAL MODEL EVALUATION")
print("=" * 65)

# --------------------------------------------------
# LOAD SELECTED MODEL
# --------------------------------------------------

artifact = joblib.load(MODEL_PATH)

model = artifact["model"]
feature_columns = artifact["feature_columns"]

if len(feature_columns) != 14:
    raise ValueError("Unexpected feature count.")

# --------------------------------------------------
# LOAD TEST DATA
# --------------------------------------------------

test_df = pd.read_csv(TEST_PATH)

required_columns = feature_columns + ["label"]

missing = [
    column for column in required_columns
    if column not in test_df.columns
]

if missing:
    raise ValueError(f"Missing test columns: {missing}")

if test_df[required_columns].isnull().any().any():
    raise ValueError("Test data contains missing values.")

if not set(test_df["label"].unique()).issubset({0, 1}):
    raise ValueError("Unexpected test labels.")

X_test = test_df[feature_columns].astype(np.float32)

# Original dataset: 0 = phishing, 1 = legitimate
# Model output: 1 = phishing, 0 = legitimate

y_test = (test_df["label"] == 0).astype(int).to_numpy()

print("\nTest records:", f"{len(X_test):,}")
print("Features:", len(feature_columns))
print("Actual phishing:", int(y_test.sum()))
print("Actual legitimate:", int((y_test == 0).sum()))

# --------------------------------------------------
# FINAL PREDICTION
# --------------------------------------------------

probabilities = model.predict_proba(X_test)[:, 1]

predictions = (
    probabilities >= SELECTED_THRESHOLD
).astype(int)

# --------------------------------------------------
# METRICS
# --------------------------------------------------

accuracy = accuracy_score(y_test, predictions)
precision = precision_score(
    y_test, predictions, zero_division=0
)
recall = recall_score(
    y_test, predictions, zero_division=0
)
f1 = f1_score(
    y_test, predictions, zero_division=0
)
roc_auc = roc_auc_score(y_test, probabilities)
pr_auc = average_precision_score(y_test, probabilities)

# Rows: actual phishing, legitimate
# Columns: predicted phishing, legitimate

cm = confusion_matrix(
    y_test,
    predictions,
    labels=[1, 0],
)

tn, fp, fn, tp = confusion_matrix(
    y_test,
    predictions,
    labels=[0, 1],
).ravel()

print("\n" + "=" * 65)
print("FINAL TEST RESULTS")
print("=" * 65)

print(f"\nThreshold: {SELECTED_THRESHOLD:.6f}")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
print(f"ROC AUC:   {roc_auc:.4f}")
print(f"PR AUC:    {pr_auc:.4f}")

print("\nConfusion Matrix")
print("Rows = Actual, Columns = Predicted")
print("Order = Phishing, Legitimate")
print(cm)

print("\nFalse negatives:", fn)
print("False positives:", fp)
print("True positives:", tp)
print("True negatives:", tn)

print("\nClassification Report")
print(
    classification_report(
        y_test,
        predictions,
        labels=[1, 0],
        target_names=["Phishing", "Legitimate"],
        zero_division=0,
    )
)

# --------------------------------------------------
# SAVE SELECTED MODEL ARTIFACT
# --------------------------------------------------

selected_model_path = (
    OUTPUT_DIR / "phishguard_x_selected.joblib"
)

joblib.dump(
    {
        "model": model,
        "feature_columns": feature_columns,
        "threshold": SELECTED_THRESHOLD,
        "model_name": "LightGBM",
        "label_mapping": {
            "model_1": "phishing",
            "model_0": "legitimate",
            "dataset_0": "phishing",
            "dataset_1": "legitimate",
        },
    },
    selected_model_path,
)

# --------------------------------------------------
# SAVE FINAL REPORT
# --------------------------------------------------

report = {
    "project": "PhishGuard X",
    "model": "LightGBM",
    "threshold": SELECTED_THRESHOLD,
    "evaluation_dataset": "test",
    "test_records": len(X_test),
    "feature_count": len(feature_columns),
    "features": feature_columns,
    "metrics": {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
    },
    "confusion_matrix": {
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
    },
}

report_path = REPORT_DIR / "final_test_results.json"

with open(report_path, "w", encoding="utf-8") as file:
    json.dump(report, file, indent=4)

print("\n" + "=" * 65)
print("FINAL MODEL SAVED")
print("=" * 65)

print("Model:", selected_model_path)
print("Report:", report_path)

print("\nFinal evaluation completed.")
