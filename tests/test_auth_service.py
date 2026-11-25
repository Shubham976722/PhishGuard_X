
from unittest.mock import MagicMock, patch

from backend.app.schemas.auth import UserRegister
from backend.app.services.auth_service import (
    register_user,
    authenticate_user
)


def create_registration_data():
    return UserRegister(
        full_name="Test User",
        email="testuser@example.com",
        password="StrongPassword123"
    )


@patch("backend.app.services.auth_service.hash_password")
def test_successful_registration(mock_hash_password):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    mock_hash_password.return_value = "hashed_password"

    def refresh_user(user):
        user.id = 1
        user.is_active = True

    db.refresh.side_effect = refresh_user

    result = register_user(db, create_registration_data())

    assert result is not None
    assert result.email == "testuser@example.com"
    assert result.hashed_password == "hashed_password"

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


def test_duplicate_email_registration():
    db = MagicMock()

    existing_user = MagicMock()
    existing_user.email = "testuser@example.com"

    db.query.return_value.filter.return_value.first.return_value = existing_user

    result = register_user(db, create_registration_data())

    assert result is None

    db.add.assert_not_called()
    db.commit.assert_not_called()


@patch("backend.app.services.auth_service.verify_password")
def test_invalid_login(mock_verify_password):
    db = MagicMock()

    user = MagicMock()
    user.hashed_password = "hashed_password"

    db.query.return_value.filter.return_value.first.return_value = user
    mock_verify_password.return_value = False

    result = authenticate_user(
        db,
        "testuser@example.com",
        "WrongPassword123"
    )

    assert result is None
    mock_verify_password.assert_called_once()


@patch("backend.app.services.auth_service.create_access_token")
@patch("backend.app.services.auth_service.verify_password")
def test_successful_authentication(
    mock_verify_password,
    mock_create_access_token
):
    db = MagicMock()

    user = MagicMock()
    user.id = 1
    user.is_active = True
    user.hashed_password = "hashed_password"

    db.query.return_value.filter.return_value.first.return_value = user

    mock_verify_password.return_value = True
    mock_create_access_token.return_value = "test_access_token"

    result = authenticate_user(
        db,
        "testuser@example.com",
        "StrongPassword123"
    )

    assert result is not None

    authenticated_user, token = result

    assert authenticated_user.id == 1
    assert token == "test_access_token"

@patch("backend.app.services.auth_service.verify_password")
def test_login_with_nonexistent_user(mock_verify_password):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    result = authenticate_user(
        db,
        "unknown@example.com",
        "StrongPassword123"
    )

    assert result is None
    mock_verify_password.assert_not_called()


@patch("backend.app.services.auth_service.verify_password")
def test_login_with_inactive_user(mock_verify_password):
    db = MagicMock()

    user = MagicMock()
    user.is_active = False
    user.hashed_password = "hashed_password"

    db.query.return_value.filter.return_value.first.return_value = user
    mock_verify_password.return_value = True

    result = authenticate_user(
        db,
        "inactive@example.com",
        "StrongPassword123"
    )

    assert result is None
    mock_verify_password.assert_called_once()
