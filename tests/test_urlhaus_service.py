
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest

from backend.app.services.urlhaus_service import (
    _prepare_urlhaus_indicator,
    sync_urlhaus,
)


def test_prepare_urlhaus_indicator_valid_url():
    record = _prepare_urlhaus_indicator(
        "HTTP://Example.com/malware"
    )

    assert record is not None
    assert record["indicator"] == "http://example.com/malware"
    assert record["hostname"] == "example.com"
    assert record["threat_type"] == "malware"
    assert record["source"] == "urlhaus"
    assert len(record["indicator_hash"]) == 64


def test_prepare_urlhaus_indicator_sets_expiration():
    before = datetime.now(timezone.utc)

    record = _prepare_urlhaus_indicator(
        "http://example.com/malware"
    )

    after = datetime.now(timezone.utc)

    assert record is not None

    expected_min = before + timedelta(days=7)
    expected_max = after + timedelta(days=7)

    assert expected_min <= record["expires_at"] <= expected_max


@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        "not-a-url",
        "",
        "ftp://example.com/file",
    ],
)
def test_prepare_urlhaus_indicator_invalid_url(url):
    assert _prepare_urlhaus_indicator(url) is None


@patch("backend.app.services.urlhaus_service.fetch_urlhaus_urls")
def test_sync_urlhaus_success(mock_fetch):
    mock_fetch.return_value = [
        "http://example.com/a",
        "http://example.com/b",
    ]

    db = MagicMock()

    result = sync_urlhaus(db)

    assert result == {
        "source": "urlhaus",
        "downloaded": 2,
        "processed": 2,
        "skipped": 0,
        "batches": 1,
    }

    assert db.execute.call_count == 1
    assert db.commit.call_count == 1


@patch("backend.app.services.urlhaus_service.fetch_urlhaus_urls")
def test_sync_urlhaus_empty_feed(mock_fetch):
    mock_fetch.return_value = []

    db = MagicMock()

    result = sync_urlhaus(db)

    assert result["downloaded"] == 0
    assert result["processed"] == 0
    assert result["batches"] == 0

    db.execute.assert_not_called()
    db.commit.assert_not_called()


@patch("backend.app.services.urlhaus_service.fetch_urlhaus_urls")
def test_sync_urlhaus_deduplicates_urls(mock_fetch):
    mock_fetch.return_value = [
        "http://example.com/a",
        "http://example.com/a",
        "http://example.com/b",
    ]

    db = MagicMock()

    result = sync_urlhaus(db)

    assert result["downloaded"] == 3
    assert result["processed"] == 2
    assert result["skipped"] == 1


@patch("backend.app.services.urlhaus_service.fetch_urlhaus_urls")
def test_sync_urlhaus_database_error_rolls_back(mock_fetch):
    mock_fetch.return_value = [
        "http://example.com/a",
    ]

    db = MagicMock()
    db.execute.side_effect = Exception("Database failure")

    with pytest.raises(Exception, match="Database failure"):
        sync_urlhaus(db)

    db.rollback.assert_called_once()


@patch("backend.app.services.urlhaus_service.fetch_urlhaus_urls")
def test_sync_urlhaus_counts_invalid_urls_as_skipped(mock_fetch):
    mock_fetch.return_value = [
        "http://example.com/valid",
        "javascript:alert(1)",
    ]

    db = MagicMock()

    result = sync_urlhaus(db)

    assert result["downloaded"] == 2
    assert result["processed"] == 1
    assert result["skipped"] == 1
    assert result["batches"] == 1

    db.execute.assert_called_once()
    db.commit.assert_called_once()


@patch("backend.app.services.urlhaus_service.fetch_urlhaus_urls")
def test_sync_urlhaus_all_invalid_urls(mock_fetch):
    mock_fetch.return_value = [
        "javascript:alert(1)",
        "ftp://example.com/file",
    ]

    db = MagicMock()

    result = sync_urlhaus(db)

    assert result["downloaded"] == 2
    assert result["processed"] == 0
    assert result["skipped"] == 2
    assert result["batches"] == 0

    db.execute.assert_not_called()
    db.commit.assert_not_called()
