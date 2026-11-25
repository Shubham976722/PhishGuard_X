from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.models.scan import Scan
from backend.app.services.ml_service import predict_url, explain_url
from backend.app.services.threat_match_service import match_threat_indicator


FEATURE_LABELS = {
    "url_length": "URL length",
    "hostname_length": "Hostname length",
    "path_length": "URL path length",
    "query_length": "URL query length",
    "count_dots": "Number of dots",
    "count_hyphens": "Number of hyphens",
    "count_at": "Number of @ symbols",
    "count_digits": "Number of digits",
    "count_percent": "Number of encoded characters",
    "count_suspicious_words": "Suspicious keywords",
    "count_subdirectories": "Number of subdirectories",
    "has_https": "HTTPS usage",
    "has_ip_address": "IP address in hostname",
    "has_punycode": "Punycode hostname",
}


def create_scan(db: Session, url: str, user_id: int | None = None):
    prediction = predict_url(url)
    probability = prediction["phishing_probability"]

    explanation_data = explain_url(url)
    threat_match = match_threat_indicator(db, url)

    verdict = prediction["verdict"]

    risk_level = (
        "high"
        if verdict == "phishing"
        else "medium"
        if probability >= 0.10
        else "low"
    )

    threat_type = "phishing" if verdict == "phishing" else None

    # Prepare structured threat metadata for database storage.
    match_type = None
    threat_sources = []
    threat_types = []

    if threat_match:
        match_type = threat_match["match_type"]
        threat_sources = threat_match["sources"]
        threat_types = threat_match["threat_types"]

        matched_threat_type = threat_match["threat_type"]

        if match_type == "exact_url":
            if matched_threat_type in ("phishing", "malware"):
                verdict = matched_threat_type
            else:
                verdict = "suspicious"

            risk_level = "high"
            threat_type = matched_threat_type

        elif match_type == "hostname":
            if verdict != "phishing":
                verdict = "suspicious"
                risk_level = "medium"

                # Hostname evidence does not establish the
                # specific threat type of this URL.
                threat_type = None

    explanation_lines = [
        f"Model: {prediction['model']}",
        f"Phishing probability: {probability * 100:.2f}%",
        "",
        "Top contributing URL features:",
    ]

    for item in explanation_data["top_factors"]:
        feature_name = FEATURE_LABELS.get(
            item["feature"],
            item["feature"],
        )

        if item["contribution"] > 0:
            impact = "increases phishing risk"
        elif item["contribution"] < 0:
            impact = "decreases phishing risk"
        else:
            impact = "has negligible impact"

        explanation_lines.append(
            f"- {feature_name}: {impact} "
            f"(contribution: {item['contribution']})"
        )

    if threat_match:
        explanation_lines.extend([
            "",
            "Threat intelligence match:",
            f"- Match type: {threat_match['match_type']}",
            f"- Threat type: {threat_match['threat_type']}",
            f"- Source: {threat_match['source']}",
            f"- Hostname: {threat_match['hostname']}",
        ])

        if threat_match["match_type"] == "hostname":
            explanation_lines.append(
                "- Warning: Hostname-only matches are not proof "
                "that every URL on this host is malicious."
            )

    else:
        explanation_lines.extend([
            "",
            "Threat intelligence: No matching indicator found.",
        ])

    explanation_lines.extend([
        "",
        "The ML probability is model output. "
        "Threat intelligence is separate external evidence.",
    ])

    explanation = "\n".join(explanation_lines)

    scan = Scan(
        user_id=user_id,
        url=url,
        risk_score=prediction["risk_score"],
        risk_level=risk_level,
        verdict=verdict,
        threat_type=threat_type,
        match_type=match_type,
        threat_sources=threat_sources,
        threat_types=threat_types,
        explanation=explanation,
    )

    try:
        db.add(scan)
        db.commit()
        db.refresh(scan)
        return scan

    except SQLAlchemyError:
        db.rollback()
        raise