
import httpx
import pytest

from unittest.mock import patch

from backend.app.integrations.threat_feeds.urlhaus import (
    fetch_urlhaus_urls,
    URLhausFeedError,
)


@patch.dict("os.environ", {"URLHAUS_AUTH_KEY": "test-api-key"})
def test_fetch_urlhaus_urls_success():
    mock_response = httpx.Response(
        200,
        json={
            "query_status": "ok",
            "urls": [
                {
                    "url": "HTTP://Malicious-Example.com/payload",
                    "url_status": "online",
                },
                {
                    "url": "http://offline-example.com/payload",
                    "url_status": "offline",
                },
                {
                    "url": "http://malicious-example.com/payload",
                    "url_status": "online",
                },
                {
                    "url": "javascript:alert(1)",
                    "url_status": "online",
                },
            ],
        },
        request=httpx.Request("GET", "https://example.com"),
    )

    with patch(
        "backend.app.integrations.threat_feeds.urlhaus.httpx.get",
        return_value=mock_response,
    ) as mock_get:
        result = fetch_urlhaus_urls()

    assert result == [
        "http://malicious-example.com/payload",
    ]

    assert mock_get.call_count == 1
    assert mock_get.call_args.kwargs["headers"]["Auth-Key"] == "test-api-key"


def test_fetch_urlhaus_missing_auth_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            URLhausFeedError,
            match="Auth-Key is not configured",
        ):
            fetch_urlhaus_urls()


@patch.dict("os.environ", {"URLHAUS_AUTH_KEY": "test-api-key"})
def test_fetch_urlhaus_http_error():
    with patch(
        "backend.app.integrations.threat_feeds.urlhaus.httpx.get",
        side_effect=httpx.ConnectError("Connection failed"),
    ):
        with pytest.raises(URLhausFeedError):
            fetch_urlhaus_urls()


@patch.dict("os.environ", {"URLHAUS_AUTH_KEY": "test-api-key"})
def test_fetch_urlhaus_invalid_json():
    mock_response = httpx.Response(
        200,
        text="invalid-json",
        request=httpx.Request("GET", "https://example.com"),
    )

    with patch(
        "backend.app.integrations.threat_feeds.urlhaus.httpx.get",
        return_value=mock_response,
    ):
        with pytest.raises(
            URLhausFeedError,
            match="invalid JSON",
        ):
            fetch_urlhaus_urls()


@patch.dict("os.environ", {"URLHAUS_AUTH_KEY": "test-api-key"})
def test_fetch_urlhaus_no_results():
    mock_response = httpx.Response(
        200,
        json={"query_status": "no_results"},
        request=httpx.Request("GET", "https://example.com"),
    )

    with patch(
        "backend.app.integrations.threat_feeds.urlhaus.httpx.get",
        return_value=mock_response,
    ):
        assert fetch_urlhaus_urls() == []


@patch.dict("os.environ", {"URLHAUS_AUTH_KEY": "test-api-key"})
def test_fetch_urlhaus_unexpected_response():
    mock_response = httpx.Response(
        200,
        json={"unexpected": "response"},
        request=httpx.Request("GET", "https://example.com"),
    )

    with patch(
        "backend.app.integrations.threat_feeds.urlhaus.httpx.get",
        return_value=mock_response,
    ):
        with pytest.raises(URLhausFeedError):
            fetch_urlhaus_urls()


@patch.dict("os.environ", {"URLHAUS_AUTH_KEY": "test-api-key"})
def test_fetch_urlhaus_invalid_entries_are_skipped():
    mock_response = httpx.Response(
        200,
        json={
            "query_status": "ok",
            "urls": [
                None,
                {"url": "javascript:alert(1)", "url_status": "online"},
                {"url": "ftp://example.com/file", "url_status": "online"},
                {"url": "http://offline.example.com", "url_status": "offline"},
            ],
        },
        request=httpx.Request("GET", "https://example.com"),
    )

    with patch(
        "backend.app.integrations.threat_feeds.urlhaus.httpx.get",
        return_value=mock_response,
    ):
        assert fetch_urlhaus_urls() == []
