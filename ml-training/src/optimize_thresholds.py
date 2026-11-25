
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
    confusion_matrix,
    precision_recall_curve,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SPLIT_DIR = PROJECT_ROOT / "ml-training" / "datasets" / "splits"
MODEL_DIR = PROJECT_ROOT / "ml-training" / "models"
REPORT_DIR = PROJECT_ROOT / "ml-training" / "reports"

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

TARGET_RECALL = 0.95

# --------------------------------------------------
# LOAD VALIDATION DATA
# --------------------------------------------------

print("=" * 65)
print("PHISHGUARD X - THRESHOLD OPTIMIZATION")
print("=" * 65)

val_df = pd.read_csv(SPLIT_DIR / "validation.csv")

X_val = val_df[FEATURE_COLUMNS].astype(np.float32)

# Original dataset: 0 = phishing, 1 = legitimate
# Model output: 1 = phishing, 0 = legitimate
y_val = (val_df["label"] == 0).astype(int).to_numpy()

models = {
    "Random Forest": (
        MODEL_DIR / "random_forest" /
        "random_forest_baseline.joblib"
    ),
    "XGBoost": (
        MODEL_DIR / "xgboost" /
        "xgboost_baseline.joblib"
    ),
    "LightGBM": (
        MODEL_DIR / "lightgbm" /
        "lightgbm_baseline.joblib"
    ),
}

all_results = {}

# --------------------------------------------------
# METRIC FUNCTION
# --------------------------------------------------

def evaluate_threshold(y_true, probabilities, threshold):
    predictions = (probabilities >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision": float(
            precision_score(y_true, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y_true, predictions, zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_true, predictions, zero_division=0)
        ),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
    }


# --------------------------------------------------
# EVALUATE MODELS
# --------------------------------------------------

for model_name, model_path in models.items():

    print("\n" + "=" * 65)
    print(model_name.upper())
    print("=" * 65)

    if not model_path.exists():
        raise FileNotFoundError(model_path)

    artifact = joblib.load(model_path)

    model = artifact["model"]
    saved_features = artifact["feature_columns"]

    if saved_features != FEATURE_COLUMNS:
        raise ValueError(
            f"Feature mismatch in {model_name}"
        )

    probabilities = model.predict_proba(X_val)[:, 1]

    precision, recall, thresholds = precision_recall_curve(
        y_val,
        probabilities,
    )

    # Best F1 threshold
    f1_values = (
        2 * precision[:-1] * recall[:-1]
        / (precision[:-1] + recall[:-1] + 1e-12)
    )

    best_f1_index = int(np.argmax(f1_values))
    best_f1_threshold = float(thresholds[best_f1_index])

    # Highest threshold that maintains target recall
    valid_indices = np.where(recall[:-1] >= TARGET_RECALL)[0]

    if len(valid_indices) > 0:
        target_index = int(valid_indices[-1])
        target_threshold = float(thresholds[target_index])

        target_result = evaluate_threshold(
            y_val,
            probabilities,
            target_threshold,
        )
    else:
        target_threshold = None
        target_result = None

    best_f1_result = evaluate_threshold(
        y_val,
        probabilities,
        best_f1_threshold,
    )

    all_results[model_name] = {
        "best_f1": best_f1_result,
        "target_recall": target_result,
    }

    print("\nBEST F1 THRESHOLD")
    for key, value in best_f1_result.items():
        print(f"{key}: {value}")

    print(f"\nTARGET RECALL: {TARGET_RECALL:.0%}")

    if target_result:
        for key, value in target_result.items():
            print(f"{key}: {value}")
    else:
        print("Target recall could not be achieved.")

# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("\n" + "=" * 65)
print("THRESHOLD OPTIMIZATION SUMMARY")
print("=" * 65)

for model_name, results in all_results.items():

    best = results["best_f1"]
    target = results["target_recall"]

    print(f"\n{model_name}")
    print(
        f"Best F1: {best['f1_score']:.4f} "
        f"at threshold {best['threshold']:.4f}"
    )

    if target:
        print(
            f"95% Recall: {target['recall']:.4f} "
            f"at threshold {target['threshold']:.4f}"
        )
        print(f"Precision: {target['precision']:.4f}")
        print(f"False negatives: {target['false_negatives']}")

# --------------------------------------------------
# SAVE REPORT
# --------------------------------------------------

report_path = REPORT_DIR / "threshold_optimization.json"

with open(report_path, "w", encoding="utf-8") as file:
    json.dump(all_results, file, indent=4)

print("\nReport saved:", report_path)
print("\nThreshold optimization completed.")
