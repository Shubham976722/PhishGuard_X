
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlsplit

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from backend.app.models.threat_indicator import ThreatIndicator
from backend.app.utils.url_normalizer import normalize_url


THREAT_PRIORITY = {
    "malware": 0,
    "phishing": 1,
}


def _build_match_result(
    match_type: str,
    records: list,
    hostname: str,
) -> dict:
    """Build a deterministic result containing all matching sources."""

    unique_matches = {
        (record.source, record.threat_type)
        for record in records
    }

    matches = [
        {
            "source": source,
            "threat_type": threat_type,
        }
        for source, threat_type in sorted(
            unique_matches,
            key=lambda item: (
                THREAT_PRIORITY.get(item[1], 99),
                item[0],
                item[1],
            ),
        )
    ]

    sources = sorted({item["source"] for item in matches})
    threat_types = sorted(
        {item["threat_type"] for item in matches},
        key=lambda item: (THREAT_PRIORITY.get(item, 99), item),
    )

    return {
        "match_type": match_type,
        "threat_type": threat_types[0],
        "source": ", ".join(sources),
        "hostname": hostname,
        "threat_types": threat_types,
        "sources": sources,
        "matches": matches,
    }


def match_threat_indicator(db: Session, url: str) -> dict | None:
    """
    Match a URL against active threat indicators.

    Matching priority:
    1. Exact normalized URL hash.
    2. Hostname match.

    All matching sources are preserved.
    Expired indicators are ignored.
    """

    try:
        normalized_url = normalize_url(url)
        parsed = urlsplit(normalized_url)
        hostname = parsed.hostname

        if not hostname:
            return None

        hostname = hostname.lower().rstrip(".")

        indicator_hash = hashlib.sha256(
            normalized_url.encode("utf-8")
        ).hexdigest()

        now = datetime.now(timezone.utc)

        active_filter = or_(
            ThreatIndicator.expires_at.is_(None),
            ThreatIndicator.expires_at > now,
        )

        # First priority: exact URL matches.
        exact_matches = (
            db.query(ThreatIndicator)
            .filter(
                and_(
                    ThreatIndicator.indicator_hash == indicator_hash,
                    active_filter,
                )
            )
            .all()
        )

        if exact_matches:
            return _build_match_result(
                match_type="exact_url",
                records=exact_matches,
                hostname=hostname,
            )

        # Second priority: hostname matches.
        # DISTINCT avoids loading every URL stored for a shared hostname.
        hostname_matches = (
            db.query(
                ThreatIndicator.source,
                ThreatIndicator.threat_type,
            )
            .filter(
                and_(
                    ThreatIndicator.hostname == hostname,
                    active_filter,
                )
            )
            .distinct()
            .all()
        )

        if hostname_matches:
            records = [
                type(
                    "ThreatMatch",
                    (),
                    {
                        "source": source,
                        "threat_type": threat_type,
                    },
                )()
                for source, threat_type in hostname_matches
            ]

            return _build_match_result(
                match_type="hostname",
                records=records,
                hostname=hostname,
            )

        return None

    except (ValueError, UnicodeError):
        return None
