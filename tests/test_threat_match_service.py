
from types import SimpleNamespace
from unittest.mock import MagicMock

from backend.app.services.threat_match_service import (
    match_threat_indicator,
)


def make_indicator(
    threat_type="phishing",
    source="phishing_database",
):
    return SimpleNamespace(
        threat_type=threat_type,
        source=source,
        hostname="malicious-example.com",
    )


def configure_hostname_results(db, exact_results, hostname_results):
    query = db.query.return_value
    query.filter.return_value.all.return_value = exact_results
    query.filter.return_value.distinct.return_value.all.return_value = (
        hostname_results
    )


def test_exact_url_match():
    db = MagicMock()

    configure_hostname_results(
        db,
        [make_indicator()],
        [],
    )

    result = match_threat_indicator(
        db,
        "https://malicious-example.com/login",
    )

    assert result["match_type"] == "exact_url"
    assert result["threat_type"] == "phishing"
    assert result["source"] == "phishing_database"
    assert result["sources"] == ["phishing_database"]
    assert db.query.call_count == 1


def test_hostname_match_when_exact_match_missing():
    db = MagicMock()

    configure_hostname_results(
        db,
        [],
        [("phishing_database", "phishing")],
    )

    result = match_threat_indicator(
        db,
        "https://malicious-example.com/another-page",
    )

    assert result["match_type"] == "hostname"
    assert result["threat_type"] == "phishing"
    assert result["source"] == "phishing_database"
    assert result["sources"] == ["phishing_database"]
    assert db.query.call_count == 2


def test_multiple_sources_are_preserved():
    db = MagicMock()

    configure_hostname_results(
        db,
        [],
        [
            ("phishing_database", "phishing"),
            ("urlhaus", "malware"),
        ],
    )

    result = match_threat_indicator(
        db,
        "https://cdn.discordapp.com/another-file",
    )

    assert result["match_type"] == "hostname"
    assert result["threat_type"] == "malware"

    assert result["sources"] == [
        "phishing_database",
        "urlhaus",
    ]

    assert result["threat_types"] == [
        "malware",
        "phishing",
    ]

    assert len(result["matches"]) == 2


def test_exact_match_from_multiple_sources():
    db = MagicMock()

    configure_hostname_results(
        db,
        [
            make_indicator("phishing", "phishing_database"),
            make_indicator("malware", "urlhaus"),
        ],
        [],
    )

    result = match_threat_indicator(
        db,
        "https://malicious-example.com/login",
    )

    assert result["match_type"] == "exact_url"
    assert result["threat_type"] == "malware"
    assert result["sources"] == [
        "phishing_database",
        "urlhaus",
    ]
    assert len(result["matches"]) == 2


def test_no_threat_match():
    db = MagicMock()

    configure_hostname_results(
        db,
        [],
        [],
    )

    result = match_threat_indicator(
        db,
        "https://example.com",
    )

    assert result is None
    assert db.query.call_count == 2


def test_invalid_url_returns_no_match():
    db = MagicMock()

    result = match_threat_indicator(
        db,
        "not-a-valid-url",
    )

    assert result is None
    db.query.assert_not_called()

from datetime import datetime, timedelta, timezone
import hashlib

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.models.threat_indicator import ThreatIndicator
from backend.app.services.threat_match_service import match_threat_indicator
from backend.app.utils.url_normalizer import normalize_url


def create_test_database():
    engine = create_engine("sqlite:///:memory:")
    ThreatIndicator.__table__.create(engine)
    return engine


def insert_test_indicator(
    db,
    url,
    expires_at,
    source="phishing_database",
    threat_type="phishing",
):
    normalized_url = normalize_url(url)

    db.add(
        ThreatIndicator(
            indicator=normalized_url,
            indicator_hash=hashlib.sha256(
                normalized_url.encode("utf-8")
            ).hexdigest(),
            hostname="expiry-example.com",
            threat_type=threat_type,
            source=source,
            last_seen=datetime.now(timezone.utc),
            expires_at=expires_at,
        )
    )
    db.commit()


def test_expired_exact_indicator_is_ignored():
    engine = create_test_database()

    try:
        with Session(engine) as db:
            url = "https://expiry-example.com/login"

            insert_test_indicator(
                db,
                url,
                datetime.now(timezone.utc) - timedelta(days=1),
            )

            result = match_threat_indicator(db, url)

            assert result is None
    finally:
        engine.dispose()


def test_expired_hostname_indicator_is_ignored():
    engine = create_test_database()

    try:
        with Session(engine) as db:
            insert_test_indicator(
                db,
                "https://expiry-example.com/old-malware",
                datetime.now(timezone.utc) - timedelta(days=1),
            )

            result = match_threat_indicator(
                db,
                "https://expiry-example.com/new-page",
            )

            assert result is None
    finally:
        engine.dispose()


def test_active_hostname_indicator_is_matched():
    engine = create_test_database()

    try:
        with Session(engine) as db:
            insert_test_indicator(
                db,
                "https://expiry-example.com/known-threat",
                datetime.now(timezone.utc) + timedelta(days=1),
            )

            result = match_threat_indicator(
                db,
                "https://expiry-example.com/another-page",
            )

            assert result is not None
            assert result["match_type"] == "hostname"
            assert result["source"] == "phishing_database"
    finally:
        engine.dispose()
