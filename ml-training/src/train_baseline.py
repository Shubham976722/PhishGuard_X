
import json
import time
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
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

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "datasets" / "splits"
MODEL_DIR = BASE_DIR / "models" / "random_forest"
REPORT_DIR = BASE_DIR / "reports"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_COLUMNS = [
    "url_length",
    "hostname_length",
    "path_length",
    "query_length",
    "count_dots",
    "count_hyphens",
    "count_at",
    "count_digits",
    "count_percent",
    "count_suspicious_words",
    "count_subdirectories",
    "has_https",
    "has_ip_address",
    "has_punycode",
]

RANDOM_STATE = 42
THRESHOLD = 0.50

# --------------------------------------------------
# LOAD AND VALIDATE DATA
# --------------------------------------------------

print("=" * 60)
print("PHISHGUARD X - RANDOM FOREST BASELINE")
print("=" * 60)

train_df = pd.read_csv(DATA_DIR / "train.csv")
val_df = pd.read_csv(DATA_DIR / "validation.csv")

for name, df in [("Training", train_df), ("Validation", val_df)]:
    required = FEATURE_COLUMNS + ["label"]

    missing_columns = set(required) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"{name} dataset is missing columns: {missing_columns}"
        )

    if df[required].isnull().any().any():
        raise ValueError(f"{name} dataset contains missing values.")

    if not set(df["label"].unique()).issubset({0, 1}):
        raise ValueError(f"{name} dataset contains invalid labels.")

    print(f"\n{name} records: {len(df):,}")

# Use only the 14 numerical URL features.
X_train = train_df[FEATURE_COLUMNS].astype("float32")
X_val = val_df[FEATURE_COLUMNS].astype("float32")

# Original mapping:
# 0 = Phishing
# 1 = Legitimate
#
# Internal model mapping:
# 1 = Phishing
# 0 = Legitimate

y_train = (train_df["label"] == 0).astype("int8")
y_val = (val_df["label"] == 0).astype("int8")

print("\nFeature count:", len(FEATURE_COLUMNS))
print("Training phishing records:", int(y_train.sum()))
print("Training legitimate records:", int((y_train == 0).sum()))

# --------------------------------------------------
# TRAIN RANDOM FOREST
# --------------------------------------------------

print("\n" + "=" * 60)
print("TRAINING RANDOM FOREST")
print("=" * 60)

model = RandomForestClassifier(
    n_estimators=300,
    max_features="sqrt",
    min_samples_split=2,
    min_samples_leaf=1,
    class_weight="balanced_subsample",
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

start_time = time.time()

model.fit(X_train, y_train)

training_seconds = time.time() - start_time

print(f"\nTraining completed in {training_seconds:.2f} seconds.")

# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

phishing_class_index = list(model.classes_).index(1)

phishing_probabilities = model.predict_proba(X_val)[
    :, phishing_class_index
]

predictions = (
    phishing_probabilities >= THRESHOLD
).astype("int8")

accuracy = accuracy_score(y_val, predictions)
precision = precision_score(y_val, predictions, zero_division=0)
recall = recall_score(y_val, predictions, zero_division=0)
f1 = f1_score(y_val, predictions, zero_division=0)

roc_auc = roc_auc_score(y_val, phishing_probabilities)
pr_auc = average_precision_score(y_val, phishing_probabilities)

# Matrix order: phishing, legitimate
matrix = confusion_matrix(
    y_val,
    predictions,
    labels=[1, 0]
)

print(f"\nThreshold: {THRESHOLD}")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
print(f"ROC AUC:   {roc_auc:.4f}")
print(f"PR AUC:    {pr_auc:.4f}")

print("\nConfusion Matrix")
print("Rows = Actual, Columns = Predicted")
print("Order = Phishing, Legitimate")
print(matrix)

print("\nClassification Report")
print(
    classification_report(
        y_val,
        predictions,
        labels=[1, 0],
        target_names=["Phishing", "Legitimate"],
        zero_division=0,
    )
)

# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

model_path = MODEL_DIR / "random_forest_baseline.joblib"

joblib.dump(
    {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "threshold": THRESHOLD,
        "positive_class": 1,
        "label_mapping": {
            "original_0": "phishing",
            "original_1": "legitimate",
            "model_0": "legitimate",
            "model_1": "phishing",
        },
    },
    model_path,
)

# --------------------------------------------------
# SAVE VALIDATION REPORT
# --------------------------------------------------

metrics = {
    "model": "RandomForestClassifier",
    "dataset": "validation",
    "training_records": len(train_df),
    "validation_records": len(val_df),
    "feature_count": len(FEATURE_COLUMNS),
    "threshold": THRESHOLD,
    "training_seconds": round(training_seconds, 2),
    "accuracy": float(accuracy),
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1),
    "roc_auc": float(roc_auc),
    "pr_auc": float(pr_auc),
    "confusion_matrix": matrix.tolist(),
}

report_path = REPORT_DIR / "random_forest_baseline.json"

with open(report_path, "w", encoding="utf-8") as file:
    json.dump(metrics, file, indent=4)

print("\n" + "=" * 60)
print("MODEL SAVED")
print("=" * 60)

print("Model:", model_path)
print("Report:", report_path)

print("\nRandom Forest baseline training completed.")
