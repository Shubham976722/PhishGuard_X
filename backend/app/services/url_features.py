import re
import ipaddress

import tldextract

from urllib.parse import urlsplit, urlunsplit


# Use bundled suffix list without network requests.
extract = tldextract.TLDExtract(
    suffix_list_urls=()
)


def extract_url_features(url: str) -> dict:

    if not isinstance(url, str) or not url.strip():
        raise ValueError("A valid URL is required.")

    url = url.strip()

    parsed = urlsplit(url)

    # Normalize equivalent root URLs for ML inference.
    if parsed.path == "/" and not parsed.query and not parsed.fragment:
        url = urlunsplit((
            parsed.scheme,
            parsed.netloc,
            "",
            parsed.query,
            parsed.fragment
        ))

        parsed = urlsplit(url)

    host = parsed.hostname or ""

    length = max(len(url), 1)

    domain_parts = extract(host)

    letters = len(re.findall(r"[a-zA-Z]", url))
    digits = len(re.findall(r"[0-9]", url))

    special_chars = len(
        re.findall(r"[^a-zA-Z0-9]", url)
    )

    try:
        ipaddress.ip_address(host)
        has_ip = 1
    except ValueError:
        has_ip = 0

    return {
        "url_length": len(url),
        "hostname_length": len(host),
        "path_length": len(parsed.path),
        "query_length": len(parsed.query),
        "tld_length": len(domain_parts.suffix),

        "subdomain_count": (
            len(domain_parts.subdomain.split("."))
            if domain_parts.subdomain else 0
        ),

        "letter_count": letters,
        "letter_ratio": letters / length,
        "digit_count": digits,
        "digit_ratio": digits / length,
        "special_char_count": special_chars,
        "special_char_ratio": special_chars / length,
        "hyphen_count": url.count("-"),
        "dot_count": url.count("."),
        "percent_count": url.count("%"),
        "at_count": url.count("@"),
        "has_ip_address": has_ip
    }