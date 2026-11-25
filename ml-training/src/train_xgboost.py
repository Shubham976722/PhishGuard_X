
import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from xgboost import XGBClassifier
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
# PATHS AND CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SPLIT_DIR = PROJECT_ROOT / "ml-training" / "datasets" / "splits"
MODEL_DIR = PROJECT_ROOT / "ml-training" / "models" / "xgboost"
REPORT_DIR = PROJECT_ROOT / "ml-training" / "reports"

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
# LOAD DATA
# --------------------------------------------------

print("=" * 60)
print("PHISHGUARD X - XGBOOST TRAINING")
print("=" * 60)

train_df = pd.read_csv(SPLIT_DIR / "train.csv")
val_df = pd.read_csv(SPLIT_DIR / "validation.csv")

for name, df in [("TRAIN", train_df), ("VALIDATION", val_df)]:
    missing_columns = [
        col for col in FEATURE_COLUMNS + ["label"]
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{name} dataset missing columns: {missing_columns}"
        )

    if df[FEATURE_COLUMNS + ["label"]].isnull().any().any():
        raise ValueError(f"{name} dataset contains missing values.")

    if not set(df["label"].unique()).issubset({0, 1}):
        raise ValueError(f"{name} dataset contains invalid labels.")

X_train = train_df[FEATURE_COLUMNS].astype(np.float32)
X_val = val_df[FEATURE_COLUMNS].astype(np.float32)

# Original dataset:
# 0 = Phishing
# 1 = Legitimate
#
# Model encoding:
# 1 = Phishing
# 0 = Legitimate

y_train = (train_df["label"] == 0).astype(int)
y_val = (val_df["label"] == 0).astype(int)

print("\nTraining records:", f"{len(X_train):,}")
print("Validation records:", f"{len(X_val):,}")
print("Feature count:", len(FEATURE_COLUMNS))
print("Training phishing records:", int(y_train.sum()))
print("Training legitimate records:", int((y_train == 0).sum()))

# --------------------------------------------------
# TRAIN XGBOOST
# --------------------------------------------------

# Give phishing examples additional weight.
scale_pos_weight = (
    (y_train == 0).sum() / max(y_train.sum(), 1)
)

model = XGBClassifier(
    n_estimators=1000,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.85,
    colsample_bytree=0.85,
    min_child_weight=2,
    reg_lambda=2,
    reg_alpha=0.1,
    objective="binary:logistic",
    eval_metric="aucpr",
    scale_pos_weight=float(scale_pos_weight),
    early_stopping_rounds=50,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    tree_method="hist",
)

print("\n" + "=" * 60)
print("TRAINING XGBOOST")
print("=" * 60)

start_time = time.time()

model.fit(
    X_train,
    y_train,
    eval_set=[(X_val, y_val)],
    verbose=False,
)

training_time = time.time() - start_time

print(f"\nTraining completed in {training_time:.2f} seconds.")
print("Best iteration:", model.best_iteration)

# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

y_prob = model.predict_proba(X_val)[:, 1]
y_pred = (y_prob >= THRESHOLD).astype(int)

accuracy = accuracy_score(y_val, y_pred)
precision = precision_score(y_val, y_pred, zero_division=0)
recall = recall_score(y_val, y_pred, zero_division=0)
f1 = f1_score(y_val, y_pred, zero_division=0)
roc_auc = roc_auc_score(y_val, y_prob)
pr_auc = average_precision_score(y_val, y_prob)

cm = confusion_matrix(y_val, y_pred, labels=[1, 0])

print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

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
print(cm)

print("\nClassification Report")
print(
    classification_report(
        y_val,
        y_pred,
        labels=[1, 0],
        target_names=["Phishing", "Legitimate"],
        zero_division=0,
    )
)

# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

model_path = MODEL_DIR / "xgboost_baseline.joblib"
report_path = REPORT_DIR / "xgboost_baseline.json"

joblib.dump(
    {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "threshold": THRESHOLD,
        "label_mapping": {
            "model_1": "phishing",
            "model_0": "legitimate",
            "dataset_0": "phishing",
            "dataset_1": "legitimate",
        },
    },
    model_path,
)

report = {
    "model": "XGBoost",
    "model_version": "3.4.1",
    "threshold": THRESHOLD,
    "training_records": len(X_train),
    "validation_records": len(X_val),
    "feature_count": len(FEATURE_COLUMNS),
    "features": FEATURE_COLUMNS,
    "training_time_seconds": round(training_time, 2),
    "best_iteration": int(model.best_iteration),
    "scale_pos_weight": float(scale_pos_weight),
    "metrics": {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
    },
    "confusion_matrix": cm.tolist(),
}

with open(report_path, "w", encoding="utf-8") as file:
    json.dump(report, file, indent=4)

print("\n" + "=" * 60)
print("MODEL SAVED")
print("=" * 60)

print("Model:", model_path)
print("Report:", report_path)

print("\nXGBoost training completed.")
