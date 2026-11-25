
import ipaddress
from urllib.parse import urlsplit, urlunsplit


SUSPICIOUS_WORDS = [
    "login", "verify", "update", "secure", "account",
    "banking", "password", "confirm", "signin",
    "wallet", "payment", "free", "bonus",
]


def extract_url_features(url: str) -> dict:
    parsed = urlsplit(url)

    hostname = (parsed.hostname or "").lower()

    # Normalize the root path
    normalized_path = "" if parsed.path == "/" else parsed.path

    normalized_url = urlunsplit((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        normalized_path,
        parsed.query,
        parsed.fragment
    ))

    full_url = normalized_url.lower()

    try:
        ipaddress.ip_address(hostname)
        has_ip_address = 1
    except ValueError:
        has_ip_address = 0

    # Dataset bias mitigation: PhiUSIIL dataset collected 100% of legitimate
    # hostnames with 'www.' (2+ dots), resulting in 0 legitimate samples with 1 dot.
    # To prevent bare apex domains (e.g. google.com, example.com) from being
    # penalized by +9.0568 log-odds, normalize 1-dot domain hostnames to 2 dots.
    raw_dots = hostname.count(".")
    count_dots = 2 if (not has_ip_address and not hostname.startswith("www.") and raw_dots == 1) else raw_dots

    return {
        "url_length": len(normalized_url),
        "hostname_length": len(hostname),
        "path_length": len(normalized_path),
        "query_length": len(parsed.query),
        "count_dots": count_dots,
        "count_hyphens": hostname.count("-"),
        "count_at": normalized_url.count("@"),
        "count_digits": sum(
            char.isdigit() for char in normalized_url
        ),
        "count_percent": normalized_url.count("%"),
        "count_suspicious_words": sum(
            word in full_url for word in SUSPICIOUS_WORDS
        ),
        "count_subdirectories": normalized_path.count("/"),
        "has_https": int(parsed.scheme.lower() == "https"),
        "has_ip_address": has_ip_address,
        "has_punycode": int("xn--" in hostname),
    }
