import json

from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

from backend.app.services.url_features import (
    extract_url_features
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_DIR = (
    PROJECT_ROOT
    / "ml-training"
    / "models"
    / "custom_v2"
)

MODEL_PATH = MODEL_DIR / "phishguard_model.txt"
METADATA_PATH = MODEL_DIR / "metadata.json"


if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}"
    )

if not METADATA_PATH.exists():
    raise FileNotFoundError(
        f"Metadata not found: {METADATA_PATH}"
    )


with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)


FEATURES = metadata["feature_columns"]
THRESHOLD = float(metadata["threshold"])
MODEL_NAME = metadata["model_name"]
MODEL_VERSION = metadata["model_version"]

DETECTION_MODE = metadata.get(
    "detection_mode", "advisory"
)

PRODUCTION_READY = metadata.get(
    "production_ready", False
)


model = lgb.Booster(
    model_file=str(MODEL_PATH)
)


if not 0.0 < THRESHOLD < 1.0:
    raise RuntimeError(
        "Invalid classification threshold."
    )

if metadata["phishing_class"] != 1:
    raise RuntimeError(
        "Invalid phishing class configuration."
    )

if metadata["legitimate_class"] != 0:
    raise RuntimeError(
        "Invalid legitimate class configuration."
    )

if model.num_feature() != len(FEATURES):
    raise RuntimeError(
        "Model feature count mismatch."
    )

if model.feature_name() != FEATURES:
    raise RuntimeError(
        "Model feature order mismatch."
    )


extractor_features = list(
    extract_url_features(
        "https://example.com"
    ).keys()
)

if FEATURES != extractor_features:
    raise RuntimeError(
        "Feature extractor mismatch."
    )


def _prepare_features(url: str):

    if not isinstance(url, str) or not url.strip():
        raise ValueError(
            "A valid URL is required."
        )

    features = extract_url_features(url)

    values = pd.DataFrame(
        [[features[name] for name in FEATURES]],
        columns=FEATURES
    )

    if not np.isfinite(values.to_numpy()).all():
        raise ValueError(
            "Invalid URL feature values."
        )

    return features, values


def predict_url(url: str) -> dict:

    _, values = _prepare_features(url)

    phishing_probability = float(
        model.predict(values)[0]
    )

    if not np.isfinite(phishing_probability):
        raise RuntimeError(
            "Invalid model prediction."
        )

    is_phishing = (
        phishing_probability >= THRESHOLD
    )

    return {
        "url": url,
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "phishing_probability": phishing_probability,
        "risk_score": round(
            phishing_probability * 100, 2
        ),
        "verdict": (
            "phishing"
            if is_phishing
            else "legitimate"
        ),
        "detection_mode": DETECTION_MODE,
        "production_ready": PRODUCTION_READY
    }


def explain_url(
    url: str,
    top_n: int = 5
) -> dict:

    if not isinstance(top_n, int) or top_n < 0:
        raise ValueError(
            "top_n must be a non-negative integer."
        )

    features, values = _prepare_features(url)

    contributions = model.predict(
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

    feature_contributions.sort(
        key=lambda item: abs(
            item["contribution"]
        ),
        reverse=True
    )

    return {
        "url": url,
        "top_factors": feature_contributions[:top_n],
        "bias": round(
            float(contributions[-1]), 4
        )
    }