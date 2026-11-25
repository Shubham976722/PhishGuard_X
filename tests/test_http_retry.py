import httpx
import pytest

from unittest.mock import Mock, patch

from backend.app.integrations.threat_feeds.http_retry import (
    request_with_retries,
    MAX_ATTEMPTS,
)


def make_response(status_code):
    request = httpx.Request("GET", "https://example.com")
    return httpx.Response(status_code, request=request)


@patch("backend.app.integrations.threat_feeds.http_retry.time.sleep")
def test_retries_after_transport_error(sleep):
    request = Mock(side_effect=[
        httpx.ConnectError("Connection failed"),
        make_response(200),
    ])

    response = request_with_retries(request)

    assert response.status_code == 200
    assert request.call_count == 2
    assert sleep.call_count == 1


@patch("backend.app.integrations.threat_feeds.http_retry.time.sleep")
def test_retries_after_server_error(sleep):
    request = Mock(side_effect=[
        make_response(503),
        make_response(200),
    ])

    response = request_with_retries(request)

    assert response.status_code == 200
    assert request.call_count == 2
    assert sleep.call_count == 1


@patch("backend.app.integrations.threat_feeds.http_retry.time.sleep")
def test_does_not_retry_authentication_error(sleep):
    request = Mock(return_value=make_response(401))

    with pytest.raises(httpx.HTTPStatusError):
        request_with_retries(request)

    assert request.call_count == 1
    sleep.assert_not_called()


@patch("backend.app.integrations.threat_feeds.http_retry.time.sleep")
def test_stops_after_maximum_attempts(sleep):
    request = Mock(
        side_effect=httpx.ConnectError("Connection failed")
    )

    with pytest.raises(httpx.ConnectError):
        request_with_retries(request)

    assert request.call_count == MAX_ATTEMPTS
    assert sleep.call_count == MAX_ATTEMPTS - 1


@patch("backend.app.integrations.threat_feeds.http_retry.time.sleep")
def test_does_not_retry_client_error(sleep):
    request = Mock(return_value=make_response(403))

    with pytest.raises(httpx.HTTPStatusError):
        request_with_retries(request)

    assert request.call_count == 1
    sleep.assert_not_called()
