import time
from collections.abc import Callable

import httpx


MAX_ATTEMPTS = 3
BACKOFF_SECONDS = 1.0
RETRYABLE_STATUS_CODES = {408, 425, 429}


def request_with_retries(
    request: Callable[[], httpx.Response],
) -> httpx.Response:
    """Retry transient HTTP failures with bounded exponential backoff."""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = request()
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            retryable = (
                status_code in RETRYABLE_STATUS_CODES
                or 500 <= status_code <= 599
            )

            if not retryable or attempt == MAX_ATTEMPTS:
                raise

        except httpx.TransportError:
            if attempt == MAX_ATTEMPTS:
                raise

        time.sleep(BACKOFF_SECONDS * (2 ** (attempt - 1)))

    raise RuntimeError("HTTP request retry loop exited unexpectedly.")
