import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.dependencies import get_current_user, get_db
from backend.app.services.ml_service import predict_url
from backend.app.services.url_features import extract_url_features

mock_user = MagicMock()
mock_user.id = 1
mock_user.full_name = "Security Test User"
mock_user.email = "security@example.com"
mock_user.is_active = True


def override_get_current_user():
    return mock_user


def override_get_db():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    yield mock_db


@pytest.fixture(autouse=True)
def override_deps():
    orig = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(orig)


client = TestClient(app)


# ==========================================
# 1. CORS Headers Verification
# ==========================================

def test_cors_allowed_origin_dashboard():
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_allowed_origin_chrome_extension():
    ext_origin = "chrome-extension://abcdefghijklmnopabcdefghijklmnop"
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": ext_origin,
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == ext_origin


def test_cors_disallowed_external_origin():
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://malicious-external-origin.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.headers.get("access-control-allow-origin") is None


# ==========================================
# 2. Security Headers Verification
# ==========================================

def test_security_headers_present():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("x-xss-protection") == "1; mode=block"
    assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"


# # ==========================================
# # 3. Apex Domain Dot Normalization
# # ==========================================

# def test_apex_domain_normalization_example_com():
#     feats = extract_url_features("https://example.com")
#     assert feats["count_dots"] == 2  # Canonicalized from 1 to 2
#     pred = predict_url("https://example.com")
#     assert pred["phishing_probability"] < 0.10
#     assert pred["verdict"] == "legitimate"


# def test_apex_domain_normalization_google_com():
#     feats = extract_url_features("https://google.com")
#     assert feats["count_dots"] == 2
#     pred = predict_url("https://google.com")
#     assert pred["phishing_probability"] < 0.10
#     assert pred["verdict"] == "legitimate"


# def test_phishing_single_dot_retains_high_risk():
#     url = "http://malicious-update-security-login.com/verify?account=1"
#     pred = predict_url(url)
#     assert pred["phishing_probability"] > 0.90
#     assert pred["verdict"] == "phishing"

# ==========================================
# 3. URL Feature and Model Verification
# ==========================================

def test_apex_domain_features_example_com():
    feats = extract_url_features("https://example.com")

    assert len(feats) == 17
    assert feats["dot_count"] == 1
    assert feats["hostname_length"] == 11
    assert feats["path_length"] == 0
    assert feats["has_ip_address"] == 0


def test_apex_domain_features_google_com():
    feats = extract_url_features("https://google.com")

    assert len(feats) == 17
    assert feats["dot_count"] == 1
    assert feats["hostname_length"] == 10
    assert feats["path_length"] == 0
    assert feats["has_ip_address"] == 0


def test_www_google_model_prediction():
    pred = predict_url("https://www.google.com")

    assert 0.0 <= pred["phishing_probability"] <= 1.0
    assert pred["phishing_probability"] < 0.10
    assert pred["verdict"] == "legitimate"
    assert pred["detection_mode"] == "advisory"
    assert pred["production_ready"] is False


def test_phishing_single_dot_retains_high_risk():
    url = "http://malicious-update-security-login.com/verify?account=1"

    pred = predict_url(url)

    assert pred["phishing_probability"] > 0.90
    assert pred["verdict"] == "phishing"
    assert pred["detection_mode"] == "advisory"


# ==========================================
# 4. Input Boundary Validation
# ==========================================

def test_oversized_url_rejected():
    oversized_url = "https://example.com/" + ("a" * 2100)
    response = client.post(
        "/api/v1/scans/",
        json={"url": oversized_url}
    )
    assert response.status_code == 422
    assert response.json()["success"] is False


def test_invalid_scheme_rejected():
    response = client.post(
        "/api/v1/scans/",
        json={"url": "javascript:alert(1)"}
    )
    assert response.status_code == 422
    assert response.json()["success"] is False


def test_empty_payload_rejected():
    response = client.post("/api/v1/scans/", json={})
    assert response.status_code == 422
    assert response.json()["success"] is False
