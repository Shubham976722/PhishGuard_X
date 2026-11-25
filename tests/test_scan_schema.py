from datetime import datetime, timezone

from backend.app.schemas.scan import ScanResponse


def test_scan_response_includes_threat_metadata():
    scan_data = {
        "id": 1,
        "user_id": 10,
        "url": "https://example.com/login",
        "risk_score": 85.0,
        "risk_level": "high",
        "verdict": "malware",
        "threat_type": "malware",
        "match_type": "exact_url",
        "threat_sources": ["urlhaus"],
        "threat_types": ["malware"],
        "explanation": "Exact URL match from URLhaus.",
        "scanned_at": datetime.now(timezone.utc),
    }

    response = ScanResponse.model_validate(scan_data)

    assert response.match_type == "exact_url"
    assert response.threat_sources == ["urlhaus"]
    assert response.threat_types == ["malware"]


def test_scan_response_without_threat_match():
    scan_data = {
        "id": 2,
        "user_id": 10,
        "url": "https://example.com/",
        "risk_score": 5.0,
        "risk_level": "low",
        "verdict": "legitimate",
        "threat_type": None,
        "match_type": None,
        "threat_sources": [],
        "threat_types": [],
        "explanation": "No matching indicator found.",
        "scanned_at": datetime.now(timezone.utc),
    }

    response = ScanResponse.model_validate(scan_data)

    assert response.match_type is None
    assert response.threat_sources == []
    assert response.threat_types == []
