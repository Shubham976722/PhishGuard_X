
import time
from collections.abc import Iterator
from urllib.parse import urlsplit

import httpx

from backend.app.integrations.threat_feeds.http_retry import (
    MAX_ATTEMPTS,
    BACKOFF_SECONDS,
    RETRYABLE_STATUS_CODES,
)


FEED_URL = (
    "https://raw.githubusercontent.com/"
    "Phishing-Database/Phishing.Database/"
    "master/phishing-links-ACTIVE.txt"
)

REQUEST_TIMEOUT = 30.0


class ThreatFeedError(Exception):
    """Raised when a threat intelligence feed cannot be retrieved."""


def _is_valid_phishing_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        return (
            parsed.scheme in ("http", "https")
            and parsed.hostname is not None
        )
    except ValueError:
        return False


def iter_phishing_urls() -> Iterator[str]:
    """Stream active phishing URLs with bounded connection retries."""

    stream_started = False

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with httpx.stream(
                "GET",
                FEED_URL,
                timeout=REQUEST_TIMEOUT,
                follow_redirects=True,
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    url = line.strip()

                    if not url or url.startswith("#"):
                        continue

                    if _is_valid_phishing_url(url):
                        stream_started = True
                        yield url

            return

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            retryable = (
                status_code in RETRYABLE_STATUS_CODES
                or 500 <= status_code <= 599
            )

            if (
                stream_started
                or not retryable
                or attempt == MAX_ATTEMPTS
            ):
                raise ThreatFeedError(
                    "Unable to retrieve the Phishing.Database feed."
                ) from exc

        except httpx.TransportError as exc:
            if stream_started or attempt == MAX_ATTEMPTS:
                raise ThreatFeedError(
                    "Unable to retrieve the Phishing.Database feed."
                ) from exc

        if attempt < MAX_ATTEMPTS:
            time.sleep(BACKOFF_SECONDS * (2 ** (attempt - 1)))


def fetch_phishing_urls() -> list[str]:
    """Download and parse the feed for tests and small diagnostics."""

    try:
        response = httpx.get(
            FEED_URL,
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
        )
        response.raise_for_status()

    except httpx.HTTPError as exc:
        raise ThreatFeedError(
            "Unable to retrieve the Phishing.Database feed."
        ) from exc

    urls = set()

    for line in response.text.splitlines():
        url = line.strip()

        if not url or url.startswith("#"):
            continue

        if _is_valid_phishing_url(url):
            urls.add(url)

    return sorted(urls)
