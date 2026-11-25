
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.dependencies import get_current_user, get_db
from backend.app.utils.security import SECRET_KEY, ALGORITHM

from backend.app.models.user import User

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

mock_user = MagicMock()
mock_user.id = 1
mock_user.full_name = "Test User"
mock_user.email = "testuser@example.com"
mock_user.is_active = True


def override_get_current_user():
    return mock_user


def override_get_db():
    yield MagicMock()


@pytest.fixture(autouse=True)
def override_dependencies():
    original_overrides = app.dependency_overrides.copy()

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_scan_requires_authentication():
    app.dependency_overrides.pop(get_current_user, None)

    response = client.post(
        "/api/v1/scans/",
        json={"url": "https://example.com"}
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@patch("backend.app.api.scans.create_scan")
def test_successful_scan_request(mock_create_scan):
    mock_scan = MagicMock()
    mock_scan.id = 1
    mock_scan.user_id = 1
    mock_scan.url = "https://example.com/"
    mock_scan.risk_score = 5.0
    mock_scan.risk_level = "low"
    mock_scan.verdict = "legitimate"
    mock_scan.threat_type = None
    mock_scan.match_type = None
    mock_scan.threat_sources = []
    mock_scan.threat_types = []
    mock_scan.explanation = "No significant phishing indicators."
    mock_scan.scanned_at = "2026-11-19T12:00:00+00:00"

    mock_create_scan.return_value = mock_scan

    response = client.post(
        "/api/v1/scans/",
        json={"url": "https://example.com"}
    )

    assert response.status_code == 201
    assert response.json()["verdict"] == "legitimate"
    assert response.json()["user_id"] == 1

    mock_create_scan.assert_called_once()


def test_invalid_url_returns_validation_error():
    response = client.post(
        "/api/v1/scans/",
        json={"url": "not-a-valid-url"}
    )

    assert response.status_code == 422

    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in body["error"]


def test_missing_url_returns_validation_error():
    response = client.post(
        "/api/v1/scans/",
        json={}
    )

    assert response.status_code == 422

    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_scan_history_filters_by_authenticated_user():
    mock_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    mock_query = mock_db.query.return_value
    mock_filtered_query = mock_query.filter.return_value
    mock_ordered_query = mock_filtered_query.order_by.return_value
    mock_offset_query = mock_ordered_query.offset.return_value
    mock_limited_query = mock_offset_query.limit.return_value

    mock_limited_query.all.return_value = []

    response = client.get("/api/v1/scans/history")

    assert response.status_code == 200
    assert response.json() == []

    # Verify that the history query applies a user ownership filter.
    filter_args = mock_query.filter.call_args.args

    assert len(filter_args) == 1
    assert "scans.user_id" in str(filter_args[0])

    # Verify default pagination.
    mock_ordered_query.offset.assert_called_once_with(0)
    mock_offset_query.limit.assert_called_once_with(20)


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
    ]
)
def test_scan_history_rejects_invalid_pagination(params):
    response = client.get(
        "/api/v1/scans/history",
        params=params
    )

    assert response.status_code == 422

    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_token_returns_401():
    app.dependency_overrides.pop(get_current_user, None)

    response = client.get(
        "/api/v1/scans/history",
        headers={"Authorization": "Bearer invalid.token.value"}
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_expired_token_returns_401():
    app.dependency_overrides.pop(get_current_user, None)

    expired_payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5)
    }

    expired_token = jwt.encode(
        expired_payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    response = client.get(
        "/api/v1/scans/history",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

@patch("backend.app.api.auth.register_user")
def test_successful_registration_endpoint(mock_register_user):
    mock_registered_user = MagicMock()
    mock_registered_user.id = 2
    mock_registered_user.full_name = "New User"
    mock_registered_user.email = "newuser@example.com"
    mock_registered_user.is_active = True

    mock_register_user.return_value = mock_registered_user

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "New User",
            "email": "newuser@example.com",
            "password": "StrongPassword123"
        }
    )

    assert response.status_code == 201
    assert response.json()["id"] == 2
    assert response.json()["email"] == "newuser@example.com"

    mock_register_user.assert_called_once()


@patch("backend.app.api.auth.register_user")
def test_duplicate_registration_endpoint(mock_register_user):
    mock_register_user.return_value = None

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "testuser@example.com",
            "password": "StrongPassword123"
        }
    )

    assert response.status_code == 409


@patch("backend.app.api.auth.authenticate_user")
def test_successful_login_endpoint(mock_authenticate_user):
    mock_authenticate_user.return_value = (
        mock_user,
        "test_access_token"
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "StrongPassword123"
        }
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "test_access_token"
    assert response.json()["token_type"] == "bearer"

    mock_authenticate_user.assert_called_once()


@patch("backend.app.api.auth.authenticate_user")
def test_invalid_login_endpoint(mock_authenticate_user):
    mock_authenticate_user.return_value = None

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401


def test_authenticated_user_profile_endpoint():
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["email"] == "testuser@example.com"
    assert response.json()["full_name"] == "Test User"


def test_liveness_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}



def test_readiness_endpoint():
    mock_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "connected"
    }

    mock_db.execute.assert_called_once()

    executed_query = mock_db.execute.call_args.args[0]

    assert str(executed_query) == "SELECT 1"

def test_readiness_endpoint_returns_503_on_database_failure():
    mock_db = MagicMock()

    mock_db.execute.side_effect = OperationalError(
        "SELECT 1",
        {},
        Exception("Database connection failed")
    )

    def failing_db():
        yield mock_db

    app.dependency_overrides[get_db] = failing_db

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "success": False,
        "error": {
            "code": "DATABASE_ERROR",
            "message": "A database operation could not be completed."
        }
    }

    mock_db.execute.assert_called_once()

# =========================
# CYBERSECURITY ASSISTANT API TESTS
# =========================

@patch("backend.app.api.assistant.answer_question")
def test_assistant_question_success(mock_answer):
    mock_answer.return_value = {
        "question": "What is phishing?",
        "answer": "Phishing is a social engineering attack.",
        "sources": []
    }

    response = client.post(
        "/api/v1/assistant/ask",
        json={"question": "What is phishing?"}
    )

    assert response.status_code == 200
    assert response.json()["answer"] == (
        "Phishing is a social engineering attack."
    )
    assert response.json()["question"] == "What is phishing?"

    mock_answer.assert_called_once_with(
        question="What is phishing?",
        top_k=3
    )


@patch("backend.app.api.assistant.answer_question")
def test_assistant_knowledge_base_unavailable(mock_answer):
    mock_answer.side_effect = FileNotFoundError()

    response = client.post(
        "/api/v1/assistant/ask",
        json={"question": "Explain phishing"}
    )

    assert response.status_code == 503
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "HTTP_503"
    assert response.json()["error"]["message"] == (
        "Cybersecurity knowledge base is not available."
    )


@patch("backend.app.api.assistant.answer_question")
def test_assistant_service_unavailable(mock_answer):
    mock_answer.side_effect = RuntimeError("Ollama unavailable")

    response = client.post(
        "/api/v1/assistant/ask",
        json={"question": "Explain phishing"}
    )

    assert response.status_code == 503
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "HTTP_503"
    assert response.json()["error"]["message"] == (
        "Cybersecurity assistant service is unavailable."
    )


@patch("backend.app.api.assistant.answer_question")
def test_assistant_invalid_operation(mock_answer):
    mock_answer.side_effect = ValueError("Invalid question")

    response = client.post(
        "/api/v1/assistant/ask",
        json={"question": "Explain phishing"}
    )

    assert response.status_code == 422
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "HTTP_422"
    assert response.json()["error"]["message"] == (
        "The assistant could not process the request."
    )


def test_assistant_rejects_short_question():
    response = client.post(
        "/api/v1/assistant/ask",
        json={"question": "ab"}
    )

    assert response.status_code == 422


@patch("backend.app.api.assistant.answer_scan_question")
def test_scan_assistant_success(mock_answer):
    mock_db = MagicMock()
    mock_scan = MagicMock()

    mock_scan.id = 10
    mock_scan.user_id = 1
    mock_scan.url = "https://example.com"
    mock_scan.verdict = "legitimate"
    mock_scan.risk_score = 5.0
    mock_scan.risk_level = "low"

    mock_db.query.return_value.filter.return_value.first.return_value = (
        mock_scan
    )

    app.dependency_overrides[get_db] = lambda: mock_db

    mock_answer.return_value = {
        "question": "Why is this URL considered legitimate?",
        "answer": "The model classified this URL as legitimate.",
        "sources": []
    }

    response = client.post(
        "/api/v1/assistant/ask-scan/10",
        json={
            "question": "Why is this URL considered legitimate?",
            "top_k": 3
        }
    )

    assert response.status_code == 200
    assert response.json()["question"] == (
        "Why is this URL considered legitimate?"
    )

    mock_answer.assert_called_once_with(
        question="Why is this URL considered legitimate?",
        scan=mock_scan,
        top_k=3
    )


def test_scan_assistant_returns_404_for_missing_or_other_user_scan():
    mock_db = MagicMock()

    mock_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/api/v1/assistant/ask-scan/999",
        json={"question": "Explain this scan"}
    )

    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "HTTP_404"
    assert response.json()["error"]["message"] == "Scan not found."


@patch("backend.app.api.assistant.answer_scan_question")
def test_scan_assistant_rejects_invalid_operation(mock_answer):
    mock_db = MagicMock()
    mock_scan = MagicMock()

    mock_scan.id = 10
    mock_scan.user_id = 1
    mock_scan.url = "https://example.com"

    mock_db.query.return_value.filter.return_value.first.return_value = (
        mock_scan
    )

    app.dependency_overrides[get_db] = lambda: mock_db

    mock_answer.side_effect = ValueError("Invalid question")

    response = client.post(
        "/api/v1/assistant/ask-scan/10",
        json={"question": "Explain this scan"}
    )

    assert response.status_code == 422
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "HTTP_422"
    assert response.json()["error"]["message"] == (
        "The assistant could not process the request."
    )


@patch("backend.app.api.scans.create_scan")
def test_public_guest_scan_succeeds_without_auth(mock_create):
    app.dependency_overrides.pop(get_current_user, None)
    mock_scan = MagicMock()
    mock_scan.id = 1
    mock_scan.user_id = None
    mock_scan.url = "https://example.com"
    mock_scan.risk_score = 0.02
    mock_scan.risk_level = "low"
    mock_scan.verdict = "legitimate"
    mock_scan.threat_type = None
    mock_scan.match_type = None
    mock_scan.threat_sources = []
    mock_scan.threat_types = []
    mock_scan.explanation = "Clean URL"
    mock_scan.scanned_at = datetime.now(timezone.utc)

    mock_create.return_value = mock_scan

    response = client.post(
        "/api/v1/scans/public",
        json={"url": "https://example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == "https://example.com"
    assert data["verdict"] == "legitimate"
    assert data["user_id"] is None


def test_scan_stats_endpoint():
    mock_db = MagicMock()
    mock_scan_1 = MagicMock()
    mock_scan_1.id = 1
    mock_scan_1.url = "https://phish.com"
    mock_scan_1.risk_score = 0.95
    mock_scan_1.risk_level = "high"
    mock_scan_1.verdict = "phishing"
    mock_scan_1.threat_type = "phishing"
    mock_scan_1.scanned_at = datetime.now(timezone.utc)

    mock_scan_2 = MagicMock()
    mock_scan_2.id = 2
    mock_scan_2.url = "https://legit.com"
    mock_scan_2.risk_score = 0.01
    mock_scan_2.risk_level = "low"
    mock_scan_2.verdict = "legitimate"
    mock_scan_2.threat_type = None
    mock_scan_2.scanned_at = datetime.now(timezone.utc)

    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        mock_scan_1, mock_scan_2
    ]
    mock_db.query.return_value.filter.return_value.count.return_value = 791218
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/v1/scans/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_scans"] == 2
    assert data["phishing_scans"] == 1
    assert data["legitimate_scans"] == 1
    assert len(data["recent_scans"]) == 2


def test_scan_export_endpoint():
    mock_db = MagicMock()
    mock_scan = MagicMock()
    mock_scan.id = 1
    mock_scan.url = "https://example.com"
    mock_scan.risk_score = 0.05
    mock_scan.risk_level = "low"
    mock_scan.verdict = "legitimate"
    mock_scan.threat_type = None
    mock_scan.match_type = None
    mock_scan.threat_sources = []
    mock_scan.explanation = "Clean"
    mock_scan.scanned_at = datetime.now(timezone.utc)

    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_scan]
    app.dependency_overrides[get_db] = lambda: mock_db

    # JSON export
    res_json = client.get("/api/v1/scans/export?format=json")
    assert res_json.status_code == 200
    assert isinstance(res_json.json(), list)
    assert res_json.json()[0]["url"] == "https://example.com"

    # CSV export
    res_csv = client.get("/api/v1/scans/export?format=csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "ID,URL,Risk Score" in res_csv.text
