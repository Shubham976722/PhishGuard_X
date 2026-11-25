from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.models.scan import Scan

from backend.app.services.ml_service import (
    predict_url,
    explain_url
)

from backend.app.services.threat_match_service import (
    match_threat_indicator
)


FEATURE_LABELS = {
    "url_length": "URL length",
    "hostname_length": "Hostname length",
    "path_length": "URL path length",
    "query_length": "URL query length",
    "tld_length": "Top-level domain length",
    "subdomain_count": "Number of subdomains",
    "letter_count": "Number of letters",
    "letter_ratio": "Letter ratio",
    "digit_count": "Number of digits",
    "digit_ratio": "Digit ratio",
    "special_char_count": "Special character count",
    "special_char_ratio": "Special character ratio",
    "hyphen_count": "Number of hyphens",
    "dot_count": "Number of dots",
    "percent_count": "Number of percent symbols",
    "at_count": "Number of @ symbols",
    "has_ip_address": "IP address in hostname"
}


def create_scan(
    db: Session,
    url: str,
    user_id: int | None = None
):

    prediction = predict_url(url)

    probability = prediction[
        "phishing_probability"
    ]

    explanation_data = explain_url(url)

    threat_match = match_threat_indicator(
        db, url
    )

    # ML predictions are advisory.
    # ML alone cannot confirm a phishing attack.

    verdict = "legitimate"
    risk_level = "low"
    threat_type = None

    if (
        prediction["verdict"] == "phishing"
        or probability >= 0.10
    ):
        verdict = "suspicious"
        risk_level = "medium"


    match_type = None
    threat_sources = []
    threat_types = []


    if threat_match:

        match_type = threat_match["match_type"]

        threat_sources = threat_match["sources"]

        threat_types = threat_match[
            "threat_types"
        ]

        matched_threat_type = threat_match[
            "threat_type"
        ]

        # Exact URL match is stronger external evidence.
        if match_type == "exact_url":

            if matched_threat_type in (
                "phishing", "malware"
            ):
                verdict = matched_threat_type
            else:
                verdict = "suspicious"

            risk_level = "high"
            threat_type = matched_threat_type

        # Hostname matches are advisory only.
        elif match_type == "hostname":

            verdict = "suspicious"
            risk_level = "medium"
            threat_type = None


    explanation_lines = [
        f"Model: {prediction['model']}",
        f"ML phishing score: {probability * 100:.2f}%",
        "Detection mode: Advisory",
        "",
        "Top contributing URL features:"
    ]


    for item in explanation_data["top_factors"]:

        feature_name = FEATURE_LABELS.get(
            item["feature"],
            item["feature"]
        )

        contribution = item["contribution"]

        if contribution > 0:
            impact = "increases the ML phishing score"

        elif contribution < 0:
            impact = "decreases the ML phishing score"

        else:
            impact = "has negligible impact"

        explanation_lines.append(
            f"- {feature_name}: {impact} "
            f"(contribution: {contribution})"
        )


    if threat_match:

        explanation_lines.extend([
            "",
            "Threat intelligence match:",
            f"- Match type: {match_type}",
            f"- Threat type: {threat_match['threat_type']}",
            f"- Source: {threat_match['source']}",
            f"- Hostname: {threat_match['hostname']}"
        ])

        if match_type == "hostname":

            explanation_lines.append(
                "- Hostname-only matches do not prove "
                "that every URL on the host is malicious."
            )

    else:

        explanation_lines.extend([
            "",
            "Threat intelligence: "
            "No matching indicator found."
        ])


    explanation_lines.extend([
        "",
        "The ML score is an experimental model output.",
        "It is not a calibrated probability of attack.",
        "ML-only predictions may contain false positives.",
        "No matching threat indicator does not guarantee safety."
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
        explanation=explanation
    )


    try:

        db.add(scan)
        db.commit()
        db.refresh(scan)

        return scan

    except SQLAlchemyError:

        db.rollback()
        raise