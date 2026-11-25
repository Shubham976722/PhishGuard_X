

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from backend.app.services.scan_service import create_scan


@patch(
    "backend.app.services.scan_service.match_threat_indicator",
    return_value=None,
)
@patch("backend.app.services.scan_service.explain_url")
@patch("backend.app.services.scan_service.predict_url")
def test_successful_scan(
    mock_predict,
    mock_explain,
    mock_threat_match,
):
    db = MagicMock()

    mock_predict.return_value = {
        "phishing_probability": 0.95,
        "risk_score": 95.0,
        "verdict": "phishing",
        "model": "LightGBM_Custom_17",
    }

    mock_explain.return_value = {
        "top_factors": [
            {
                "feature": "dot_count",
                "contribution": 0.25,
            }
        ]
    }

    def refresh_scan(scan):
        scan.id = 1

    db.refresh.side_effect = refresh_scan

    result = create_scan(
        db=db,
        url="https://suspicious-example.com/login",
        user_id=1,
    )

    assert result.id == 1
    assert result.user_id == 1
    assert result.verdict == "suspicious"
    assert result.risk_level == "medium"
    assert result.risk_score == 95.0
    assert result.threat_type is None
    assert result.match_type is None
    assert result.threat_sources == []
    assert result.threat_types == []

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


@patch(
    "backend.app.services.scan_service.match_threat_indicator",
    return_value=None,
)
@patch("backend.app.services.scan_service.explain_url")
@patch("backend.app.services.scan_service.predict_url")
def test_low_risk_scan(
    mock_predict,
    mock_explain,
    mock_threat_match,
):
    db = MagicMock()

    mock_predict.return_value = {
        "phishing_probability": 0.05,
        "risk_score": 5.0,
        "verdict": "legitimate",
        "model": "LightGBM",
    }

    mock_explain.return_value = {
        "top_factors": []
    }

    result = create_scan(
        db=db,
        url="https://example.com",
        user_id=1,
    )

    assert result.verdict == "legitimate"
    assert result.risk_level == "low"
    assert result.threat_type is None
    assert result.match_type is None
    assert result.threat_sources == []
    assert result.threat_types == []

    db.commit.assert_called_once()


@patch(
    "backend.app.services.scan_service.match_threat_indicator",
    return_value=None,
)
@patch("backend.app.services.scan_service.explain_url")
@patch("backend.app.services.scan_service.predict_url")
def test_scan_database_failure_rolls_back(
    mock_predict,
    mock_explain,
    mock_threat_match,
):
    db = MagicMock()

    mock_predict.return_value = {
        "phishing_probability": 0.95,
        "risk_score": 95.0,
        "verdict": "phishing",
        "model": "LightGBM",
    }

    mock_explain.return_value = {
        "top_factors": []
    }

    db.commit.side_effect = SQLAlchemyError(
        "Simulated database failure"
    )

    with pytest.raises(SQLAlchemyError):
        create_scan(
            db=db,
            url="https://suspicious-example.com",
            user_id=1,
        )

    db.rollback.assert_called_once()


@patch(
    "backend.app.services.scan_service.match_threat_indicator"
)
@patch("backend.app.services.scan_service.explain_url")
@patch("backend.app.services.scan_service.predict_url")
def test_exact_malware_match(
    mock_predict,
    mock_explain,
    mock_threat_match,
):
    db = MagicMock()

    mock_predict.return_value = {
        "phishing_probability": 0.05,
        "risk_score": 5.0,
        "verdict": "legitimate",
        "model": "LightGBM",
    }

    mock_explain.return_value = {
        "top_factors": []
    }

    mock_threat_match.return_value = {
        "match_type": "exact_url",
        "threat_type": "malware",
        "source": "urlhaus",
        "sources": ["urlhaus"],
        "threat_types": ["malware"],
        "hostname": "malware-example.com",
    }

    result = create_scan(
        db=db,
        url="http://malware-example.com/payload",
        user_id=1,
    )

    assert result.verdict == "malware"
    assert result.risk_level == "high"
    assert result.threat_type == "malware"
    assert result.risk_score == 5.0
    assert result.match_type == "exact_url"
    assert result.threat_sources == ["urlhaus"]
    assert result.threat_types == ["malware"]
    assert "urlhaus" in result.explanation

    db.commit.assert_called_once()


@patch(
    "backend.app.services.scan_service.match_threat_indicator"
)
@patch("backend.app.services.scan_service.explain_url")
@patch("backend.app.services.scan_service.predict_url")
def test_hostname_only_malware_match(
    mock_predict,
    mock_explain,
    mock_threat_match,
):
    db = MagicMock()

    mock_predict.return_value = {
        "phishing_probability": 0.05,
        "risk_score": 5.0,
        "verdict": "legitimate",
        "model": "LightGBM",
    }

    mock_explain.return_value = {
        "top_factors": []
    }

    mock_threat_match.return_value = {
        "match_type": "hostname",
        "threat_type": "malware",
        "source": "urlhaus",
        "sources": ["urlhaus"],
        "threat_types": ["malware"],
        "hostname": "malware-example.com",
    }

    result = create_scan(
        db=db,
        url="http://malware-example.com/another-page",
        user_id=1,
    )

    assert result.verdict == "suspicious"
    assert result.risk_level == "medium"
    assert result.threat_type is None
    assert result.risk_score == 5.0
    assert result.match_type == "hostname"
    assert result.threat_sources == ["urlhaus"]
    assert result.threat_types == ["malware"]
    assert "urlhaus" in result.explanation
    assert "Hostname-only matches" in result.explanation

    db.commit.assert_called_once()

