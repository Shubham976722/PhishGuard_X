
from pathlib import Path
import pandas as pd

import joblib
import numpy as np

from backend.app.services.url_features import extract_url_features


# Project root: PhishGuard_X
PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml-training"
    / "models"
    / "selected"
    / "phishguard_x_selected.joblib"
)


# Load the selected model artifact once.
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Selected model artifact not found: {MODEL_PATH}"
    )

artifact = joblib.load(MODEL_PATH)

if not isinstance(artifact, dict):
    raise RuntimeError("Invalid model artifact format.")

model = artifact["model"]
FEATURES = artifact["feature_columns"]
THRESHOLD = float(artifact["threshold"])
MODEL_NAME = artifact["model_name"]

if not hasattr(model, "booster_"):
    raise RuntimeError("Loaded model does not expose a trained LightGBM Booster.")

if not 0.0 <= THRESHOLD <= 1.0:
    raise RuntimeError("Invalid classification threshold.")

# Ensure training and inference feature names and order match.
extractor_features = list(
    extract_url_features("https://example.com").keys()
)

if FEATURES != extractor_features:
    raise RuntimeError(
        "Feature mismatch between model artifact and URL feature extractor."
    )


def _prepare_features(url: str):
    if not isinstance(url, str) or not url.strip():
        raise ValueError("A valid URL is required.")

    features = extract_url_features(url)

    values = pd.DataFrame(
    [[features[name] for name in FEATURES]],
    columns=FEATURES
)

    return features, values


def predict_url(url: str) -> dict:
    features, values = _prepare_features(url)

    # Use LightGBM's native Booster API.
    # This avoids the blocked scikit-learn wrapper.
    phishing_probability = float(
        model.booster_.predict(values)[0]
    )

    is_phishing = phishing_probability >= THRESHOLD

    return {
        "url": url,
        "model": MODEL_NAME,
        "phishing_probability": round(phishing_probability, 4),
        "risk_score": round(phishing_probability * 100, 2),
        "verdict": "phishing" if is_phishing else "legitimate"
    }



def explain_url(url: str, top_n: int = 5) -> dict:
    features, values = _prepare_features(url)

    if not isinstance(top_n, int) or top_n < 0:
        raise ValueError("top_n must be a non-negative integer.")

    # LightGBM contributions are returned in raw-score space.
    contributions = model.booster_.predict(
        values,
        pred_contrib=True
    )[0]

    feature_contributions = []

    for index, name in enumerate(FEATURES):
        feature_contributions.append({
            "feature": name,
            "value": features[name],
            "contribution": round(
                float(contributions[index]), 4
            )
        })

    # Positive contributions increase the phishing score.
    # Negative contributions decrease the phishing score.
    feature_contributions.sort(
        key=lambda item: abs(item["contribution"]),
        reverse=True
    )

    return {
        "url": url,
        "top_factors": feature_contributions[:top_n],
        "bias": round(float(contributions[-1]), 4)
    }
