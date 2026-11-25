
import hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.app.models.threat_indicator import ThreatIndicator
from backend.app.integrations.threat_feeds.urlhaus import (
    fetch_urlhaus_urls,
)
from backend.app.utils.url_normalizer import normalize_url


BATCH_SIZE = 1000
SOURCE_NAME = "urlhaus"
THREAT_TYPE = "malware"
INDICATOR_TTL_DAYS = 7


def _prepare_urlhaus_indicator(url: str) -> dict | None:
    """Validate and prepare a normalized URLhaus malware indicator."""

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
            "expires_at": now + timedelta(days=INDICATOR_TTL_DAYS),
        }

    except (ValueError, UnicodeError):
        return None



def sync_urlhaus(db: Session) -> dict:
    """Fetch and upsert URLhaus malware indicators in batches."""

    downloaded = 0
    processed = 0
    skipped = 0
    committed_batches = 0

    try:
        urls = fetch_urlhaus_urls()
        downloaded = len(urls)

        seen = set()
        batch_urls = []

        for url in urls:
            if url in seen:
                skipped += 1
                continue

            seen.add(url)
            batch_urls.append(url)

            if len(batch_urls) >= BATCH_SIZE:
                processed_batch, skipped_batch = _commit_batch(
                    db, batch_urls
                )
                processed += processed_batch
                skipped += skipped_batch

                if processed_batch:
                    committed_batches += 1

                batch_urls = []

        # Process remaining URLs after the loop.
        if batch_urls:
            processed_batch, skipped_batch = _commit_batch(
                db, batch_urls
            )
            processed += processed_batch
            skipped += skipped_batch

            if processed_batch:
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


def _commit_batch(db: Session, urls: list[str]) -> tuple[int, int]:
    """Insert or update one batch and return processed/skipped counts."""

    records = []
    skipped = 0

    for url in urls:
        record = _prepare_urlhaus_indicator(url)

        if record is None:
            skipped += 1
            continue

        records.append(record)

    if not records:
        return 0, skipped

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

    return len(records), skipped
