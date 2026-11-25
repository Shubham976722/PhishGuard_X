
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from backend.app.services.threat_intel_service import (
    _prepare_indicator,
    sync_phishing_database,
)


def test_prepare_indicator_valid_url():
    before = datetime.now(timezone.utc)

    result = _prepare_indicator(
        "https://Malicious-Example.com/login"
    )

    after = datetime.now(timezone.utc)

    assert result is not None
    assert result["hostname"] == "malicious-example.com"
    assert result["threat_type"] == "phishing"
    assert result["source"] == "phishing_database"
    assert len(result["indicator_hash"]) == 64

    assert result["expires_at"] is not None
    assert before + timedelta(days=7) <= result["expires_at"]
    assert result["expires_at"] <= after + timedelta(days=7)


def test_prepare_indicator_invalid_url():
    assert _prepare_indicator("not-a-valid-url") is None


def test_sync_phishing_database_success():
    mock_db = MagicMock()

    urls = [
        "https://bad-example.com/login",
        "https://malicious-example.net/account",
        "invalid-url",
    ]

    with patch(
        "backend.app.services.threat_intel_service.iter_phishing_urls",
        return_value=iter(urls),
    ):
        result = sync_phishing_database(mock_db)

    assert result["downloaded"] == 3
    assert result["processed"] == 2
    assert result["skipped"] == 1
    assert result["batches"] == 1

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.rollback.assert_not_called()


def test_sync_phishing_database_empty_feed():
    mock_db = MagicMock()

    with patch(
        "backend.app.services.threat_intel_service.iter_phishing_urls",
        return_value=iter([]),
    ):
        result = sync_phishing_database(mock_db)

    assert result["downloaded"] == 0
    assert result["processed"] == 0
    assert result["batches"] == 0

    mock_db.execute.assert_not_called()
    mock_db.commit.assert_not_called()


def test_sync_phishing_database_database_error():
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("Database failure")

    with patch(
        "backend.app.services.threat_intel_service.iter_phishing_urls",
        return_value=iter(["https://bad-example.com/login"]),
    ):
        with pytest.raises(Exception, match="Database failure"):
            sync_phishing_database(mock_db)

    mock_db.rollback.assert_called_once()
    mock_db.commit.assert_not_called()


def test_sync_phishing_database_commits_multiple_batches():
    mock_db = MagicMock()

    urls = [
        f"https://example-{i}.invalid/login"
        for i in range(1001)
    ]

    with patch(
        "backend.app.services.threat_intel_service.iter_phishing_urls",
        return_value=iter(urls),
    ):
        result = sync_phishing_database(mock_db)

    assert result["downloaded"] == 1001
    assert result["processed"] == 1001
    assert result["batches"] == 2
    assert mock_db.execute.call_count == 2
    assert mock_db.commit.call_count == 2


def test_sync_phishing_database_deduplicates_within_batch():
    mock_db = MagicMock()

    urls = [
        "https://duplicate-example.invalid/login",
        "https://duplicate-example.invalid/login",
    ]

    with patch(
        "backend.app.services.threat_intel_service.iter_phishing_urls",
        return_value=iter(urls),
    ):
        result = sync_phishing_database(mock_db)

    assert result["downloaded"] == 2
    assert result["processed"] == 1
    assert result["skipped"] == 1
    assert result["batches"] == 1


def test_sync_preserves_committed_batches_after_later_failure():
    mock_db = MagicMock()

    mock_db.execute.side_effect = [
        None,
        Exception("Simulated second-batch failure"),
    ]

    urls = [
        f"https://example-{i}.invalid/login"
        for i in range(1001)
    ]

    with patch(
        "backend.app.services.threat_intel_service.iter_phishing_urls",
        return_value=iter(urls),
    ):
        with pytest.raises(
            Exception,
            match="Simulated second-batch failure",
        ):
            sync_phishing_database(mock_db)

    assert mock_db.execute.call_count == 2
    assert mock_db.commit.call_count == 1
    assert mock_db.rollback.call_count == 1
