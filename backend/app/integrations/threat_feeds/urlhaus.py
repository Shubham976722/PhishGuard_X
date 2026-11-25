import os
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from dotenv import load_dotenv

from backend.app.utils.url_normalizer import normalize_url
from backend.app.integrations.threat_feeds.http_retry import (
    request_with_retries,
)


ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=ENV_FILE)

API_URL = "https://urlhaus-api.abuse.ch/v1/urls/recent/"
REQUEST_TIMEOUT = 30.0


class URLhausFeedError(Exception):
    """Raised when the URLhaus feed cannot be retrieved or parsed."""


def _is_valid_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        return (
            parsed.scheme in ("http", "https")
            and parsed.hostname is not None
        )
    except ValueError:
        return False


def fetch_urlhaus_urls() -> list[str]:
    """
    Retrieve recent online malware URLs from URLhaus.

    Only URLs currently reported as online are returned.
    Results are normalized and deduplicated.
    """

    auth_key = os.getenv("URLHAUS_AUTH_KEY")

    if not auth_key:
        raise URLhausFeedError(
            "URLhaus Auth-Key is not configured."
        )

    headers = {
        "Auth-Key": auth_key,
        "Accept": "application/json",
    }

    try:
        response = request_with_retries(
            lambda: httpx.get(
                API_URL,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
        )

        data = response.json()

    except httpx.HTTPError as exc:
        raise URLhausFeedError(
            "Unable to retrieve the URLhaus feed."
        ) from exc

    except ValueError as exc:
        raise URLhausFeedError(
            "URLhaus returned an invalid JSON response."
        ) from exc

    if not isinstance(data, dict):
        raise URLhausFeedError(
            "URLhaus returned an unexpected response."
        )

    query_status = data.get("query_status")

    if query_status == "no_results":
        return []

    if query_status != "ok":
        raise URLhausFeedError(
            f"URLhaus query failed: {query_status}"
        )

    entries = data.get("urls")

    if not isinstance(entries, list):
        raise URLhausFeedError(
            "URLhaus response does not contain a valid URL list."
        )

    urls = set()

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        if entry.get("url_status") != "online":
            continue

        url = entry.get("url")

        if not isinstance(url, str) or not _is_valid_url(url):
            continue

        try:
            normalized_url = normalize_url(url)
            urls.add(normalized_url)
        except (ValueError, UnicodeError):
            continue

    return sorted(urls)
