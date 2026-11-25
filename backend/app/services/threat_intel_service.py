
import hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.app.models.threat_indicator import ThreatIndicator
from backend.app.integrations.threat_feeds.phishing_database import (
    iter_phishing_urls,
)
from backend.app.utils.url_normalizer import normalize_url


BATCH_SIZE = 1000
SOURCE_NAME = "phishing_database"
THREAT_TYPE = "phishing"
INDICATOR_TTL_DAYS = 7


def _prepare_indicator(url: str) -> dict | None:
    """Validate and prepare a normalized phishing indicator."""

    try:
        normalized_url = normalize_url(url)
        parsed = urlsplit(normalized_url)
        hostname = parsed.hostname

        if not hostname:
            return None

        hostname = hostname.lower().rstrip(".")

        if len(hostname) > 255:
            return None

        now = datetime.now(timezone.utc)

        indicator_hash = hashlib.sha256(
            normalized_url.encode("utf-8")
        ).hexdigest()

        return {
            "indicator": normalized_url,
            "indicator_hash": indicator_hash,
            "hostname": hostname,
            "threat_type": THREAT_TYPE,
            "source": SOURCE_NAME,
            "first_seen": None,
            "last_seen": now,
            "expires_at": now + timedelta(
                days=INDICATOR_TTL_DAYS
            ),
        }

    except (ValueError, UnicodeError):
        return None


def sync_phishing_database(db: Session) -> dict:
    """Stream and upsert phishing indicators in deduplicated batches."""

    downloaded = 0
    processed = 0
    skipped = 0
    committed_batches = 0

    batch_records = []
    seen_hashes = set()

    def commit_batch(records: list[dict]) -> int:
        if not records:
            return 0

        statement = insert(ThreatIndicator).values(records)

        statement = statement.on_conflict_do_update(
            constraint="uq_threat_indicator_hash_source",
            set_={
                "hostname": statement.excluded.hostname,
                "threat_type": statement.excluded.threat_type,
                "last_seen": statement.excluded.last_seen,
                "expires_at": statement.excluded.expires_at,
            },
        )

        db.execute(statement)
        db.commit()

        return len(records)

    try:
        for url in iter_phishing_urls():
            downloaded += 1

            record = _prepare_indicator(url)

            if record is None:
                skipped += 1
                continue

            indicator_hash = record["indicator_hash"]

            if indicator_hash in seen_hashes:
                skipped += 1
                continue

            seen_hashes.add(indicator_hash)
            batch_records.append(record)

            if len(batch_records) >= BATCH_SIZE:
                batch_processed = commit_batch(batch_records)

                processed += batch_processed

                if batch_processed:
                    committed_batches += 1

                batch_records = []
                seen_hashes.clear()

        if batch_records:
            batch_processed = commit_batch(batch_records)

            processed += batch_processed

            if batch_processed:
                committed_batches += 1

    except Exception:
        db.rollback()
        raise

    return {
        "source": SOURCE_NAME,
        "downloaded": downloaded,
        "processed": processed,
        "skipped": skipped,
        "batches": committed_batches,
    }
