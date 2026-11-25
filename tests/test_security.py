
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from backend.app.utils.security import (
    SECRET_KEY,
    ALGORITHM,
    create_access_token,
    hash_password,
    verify_password
)


def test_password_hashing():
    password = "StrongPassword123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("WrongPassword123", hashed_password)


def test_access_token_creation_and_decoding():
    token = create_access_token(1)

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    assert payload["sub"] == "1"
    assert "exp" in payload


def test_expired_token_is_rejected():
    expired_payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5)
    }

    expired_token = jwt.encode(
        expired_payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(
            expired_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )


def test_tampered_token_is_rejected():
    token = create_access_token(1)

    tampered_token = token[:-5] + "abcde"

    with pytest.raises(jwt.InvalidTokenError):
        jwt.decode(
            tampered_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
