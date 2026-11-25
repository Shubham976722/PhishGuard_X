
import httpx
import pytest

from unittest.mock import patch
from unittest.mock import MagicMock

from backend.app.integrations.threat_feeds.phishing_database import (
    fetch_phishing_urls,
    ThreatFeedError,
)


def test_fetch_phishing_urls_success():
    feed_content = """
https://malicious-example.com/login
http://bad-example.net/update
https://malicious-example.com/login

# This is a comment
javascript:alert(1)
not-a-valid-url
ftp://example.com/file
"""

    mock_response = httpx.Response(
        200,
        text=feed_content,
        request=httpx.Request("GET", "https://example.com")
    )

    with patch(
        "backend.app.integrations.threat_feeds.phishing_database.httpx.get",
        return_value=mock_response
    ):
        result = fetch_phishing_urls()

    assert result == [
        "http://bad-example.net/update",
        "https://malicious-example.com/login",
    ]


def test_fetch_phishing_urls_empty_feed():
    mock_response = httpx.Response(
        200,
        text="",
        request=httpx.Request("GET", "https://example.com")
    )

    with patch(
        "backend.app.integrations.threat_feeds.phishing_database.httpx.get",
        return_value=mock_response
    ):
        result = fetch_phishing_urls()

    assert result == []


def test_fetch_phishing_urls_http_error():
    with patch(
        "backend.app.integrations.threat_feeds.phishing_database.httpx.get",
        side_effect=httpx.ConnectError("Connection failed")
    ):
        with pytest.raises(ThreatFeedError):
            fetch_phishing_urls()


def test_iter_phishing_urls_success():
    from backend.app.integrations.threat_feeds.phishing_database import (
        iter_phishing_urls,
    )

    mock_response = MagicMock()
    mock_response.iter_lines.return_value = [
        "https://malicious-example.com/login",
        "",
        "# comment",
        "javascript:alert(1)",
        "http://bad-example.net/update",
    ]

    with patch(
        "backend.app.integrations.threat_feeds.phishing_database.httpx.stream"
    ) as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        result = list(iter_phishing_urls())

    assert result == [
        "https://malicious-example.com/login",
        "http://bad-example.net/update",
    ]

    mock_response.raise_for_status.assert_called_once()


def test_iter_phishing_urls_network_error():
    from backend.app.integrations.threat_feeds.phishing_database import (
        iter_phishing_urls,
    )

    with patch(
        "backend.app.integrations.threat_feeds.phishing_database.httpx.stream",
        side_effect=httpx.ConnectError("Connection failed"),
    ):
        with pytest.raises(ThreatFeedError):
            list(iter_phishing_urls())

def test_iter_phishing_urls_does_not_retry_after_stream_starts():
    from backend.app.integrations.threat_feeds.phishing_database import (
        iter_phishing_urls,
    )

    mock_response = MagicMock()

    def broken_stream():
        yield "https://malicious-example.com/login"
        raise httpx.ReadError("Connection interrupted")

    mock_response.iter_lines.side_effect = broken_stream

    with (
        patch(
            "backend.app.integrations.threat_feeds.phishing_database.httpx.stream"
        ) as mock_stream,
        patch(
            "backend.app.integrations.threat_feeds.phishing_database.time.sleep"
        ) as mock_sleep,
    ):
        mock_stream.return_value.__enter__.return_value = mock_response

        iterator = iter_phishing_urls()

        assert next(iterator) == "https://malicious-example.com/login"

        with pytest.raises(ThreatFeedError):
            next(iterator)

    mock_stream.assert_called_once()
    mock_sleep.assert_not_called()
