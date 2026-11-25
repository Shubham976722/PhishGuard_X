
from urllib.parse import urlsplit, urlunsplit


def normalize_url(url: str) -> str:
    """
    Normalize URLs consistently before threat-indicator hashing.

    Normalization:
    - Lowercase the scheme and hostname.
    - Remove trailing dots from the hostname.
    - Use '/' when the URL has an empty path.
    - Preserve query strings and fragments.
    """
    try:
        parsed = urlsplit(url)

        scheme = parsed.scheme.lower()
        hostname = parsed.hostname

        if scheme not in ("http", "https") or not hostname:
            raise ValueError("Invalid HTTP or HTTPS URL")

        hostname = hostname.lower().rstrip(".")

        if not hostname:
            raise ValueError("Invalid hostname")

        # Preserve an explicitly supplied port.
        port = parsed.port

        if ":" in hostname:  # IPv6 address
            hostname = f"[{hostname}]"

        netloc = hostname

        if port is not None:
            netloc = f"{netloc}:{port}"

        path = parsed.path or "/"

        return urlunsplit((
            scheme,
            netloc,
            path,
            parsed.query,
            parsed.fragment,
        ))

    except (ValueError, UnicodeError) as exc:
        raise ValueError("Unable to normalize URL") from exc
