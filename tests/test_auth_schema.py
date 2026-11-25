
import pytest
from pydantic import ValidationError

from backend.app.schemas.auth import UserRegister, UserLogin


def test_registration_trims_full_name():
    user = UserRegister(
        full_name="  John Smith  ",
        email="john@example.com",
        password="StrongPass123"
    )

    assert user.full_name == "John Smith"


@pytest.mark.parametrize(
    "full_name",
    ["", " ", "   ", " A "]
)
def test_registration_rejects_invalid_full_name(full_name):
    with pytest.raises(ValidationError):
        UserRegister(
            full_name=full_name,
            email="john@example.com",
            password="StrongPass123"
        )


def test_registration_rejects_password_over_128_characters():
    with pytest.raises(ValidationError):
        UserRegister(
            full_name="John Smith",
            email="john@example.com",
            password="A" * 129
        )


def test_login_rejects_empty_password():
    with pytest.raises(ValidationError):
        UserLogin(
            email="john@example.com",
            password=""
        )


def test_login_rejects_password_over_128_characters():
    with pytest.raises(ValidationError):
        UserLogin(
            email="john@example.com",
            password="A" * 129
        )
