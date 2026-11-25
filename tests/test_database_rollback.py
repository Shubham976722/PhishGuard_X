
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from backend.app.api.dependencies import get_db


def test_database_session_rolls_back_on_exception(monkeypatch):
    mock_db = MagicMock()

    monkeypatch.setattr(
        "backend.app.api.dependencies.SessionLocal",
        lambda: mock_db
    )

    generator = get_db()

    # Start the dependency and obtain the mocked session.
    session = next(generator)

    assert session is mock_db

    # Simulate an endpoint raising an exception.
    with pytest.raises(RuntimeError):
        generator.throw(RuntimeError("Simulated database failure"))

    # Verify rollback and cleanup.
    mock_db.rollback.assert_called_once()
    mock_db.close.assert_called_once()


def test_database_session_closes_on_success(monkeypatch):
    mock_db = MagicMock()

    monkeypatch.setattr(
        "backend.app.api.dependencies.SessionLocal",
        lambda: mock_db
    )

    generator = get_db()

    session = next(generator)

    assert session is mock_db

    # Simulate a successful request.
    with pytest.raises(StopIteration):
        next(generator)

    mock_db.rollback.assert_not_called()
    mock_db.close.assert_called_once()
