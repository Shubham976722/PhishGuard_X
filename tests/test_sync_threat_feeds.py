from unittest.mock import MagicMock

import backend.scripts.sync_threat_feeds as sync_script


def test_all_feeds_sync_successfully(monkeypatch):
    db_sessions = [MagicMock(), MagicMock()]
    session_factory = iter(db_sessions)

    monkeypatch.setattr(
        sync_script,
        "SessionLocal",
        lambda: next(session_factory),
    )

    phishing_sync = MagicMock(return_value={"source": "phishing_database", "downloaded": 100, "processed": 100, "skipped": 0, "batches": 1})
    urlhaus_sync = MagicMock(return_value={"source": "urlhaus", "downloaded": 50, "processed": 50, "skipped": 0, "batches": 1})

    monkeypatch.setattr(
        sync_script,
        "sync_phishing_database",
        phishing_sync,
    )
    monkeypatch.setattr(
        sync_script,
        "sync_urlhaus",
        urlhaus_sync,
    )

    result = sync_script.main()

    assert result == 0
    phishing_sync.assert_called_once_with(db_sessions[0])
    urlhaus_sync.assert_called_once_with(db_sessions[1])

    for db in db_sessions:
        db.close.assert_called_once()


def test_second_feed_runs_when_first_feed_fails(monkeypatch):
    db_sessions = [MagicMock(), MagicMock()]
    session_factory = iter(db_sessions)

    monkeypatch.setattr(
        sync_script,
        "SessionLocal",
        lambda: next(session_factory),
    )

    phishing_sync = MagicMock(
        side_effect=RuntimeError("Phishing feed unavailable")
    )
    urlhaus_sync = MagicMock(return_value={"source": "urlhaus", "downloaded": 50, "processed": 50, "skipped": 0, "batches": 1})

    monkeypatch.setattr(
        sync_script,
        "sync_phishing_database",
        phishing_sync,
    )
    monkeypatch.setattr(
        sync_script,
        "sync_urlhaus",
        urlhaus_sync,
    )

    result = sync_script.main()

    assert result == 1
    phishing_sync.assert_called_once()
    urlhaus_sync.assert_called_once()

    for db in db_sessions:
        db.close.assert_called_once()


def test_failed_second_feed_returns_failure(monkeypatch):
    db_sessions = [MagicMock(), MagicMock()]
    session_factory = iter(db_sessions)

    monkeypatch.setattr(
        sync_script,
        "SessionLocal",
        lambda: next(session_factory),
    )

    phishing_sync = MagicMock(return_value={"source": "phishing_database", "downloaded": 100, "processed": 100, "skipped": 0, "batches": 1})
    urlhaus_sync = MagicMock(
        side_effect=RuntimeError("URLhaus unavailable")
    )

    monkeypatch.setattr(
        sync_script,
        "sync_phishing_database",
        phishing_sync,
    )
    monkeypatch.setattr(
        sync_script,
        "sync_urlhaus",
        urlhaus_sync,
    )

    result = sync_script.main()

    assert result == 1
    phishing_sync.assert_called_once()
    urlhaus_sync.assert_called_once()

    for db in db_sessions:
        db.close.assert_called_once()
def test_session_creation_failure_does_not_stop_next_feed(monkeypatch):
    failed_db = MagicMock()

    def session_factory():
        if not hasattr(session_factory, "called"):
            session_factory.called = True
            raise RuntimeError("Database unavailable")
        return failed_db

    monkeypatch.setattr(
        sync_script,
        "SessionLocal",
        session_factory,
    )

    phishing_sync = MagicMock()
    urlhaus_sync = MagicMock(return_value={"source": "urlhaus", "downloaded": 50, "processed": 50, "skipped": 0, "batches": 1})

    monkeypatch.setattr(
        sync_script,
        "sync_phishing_database",
        phishing_sync,
    )
    monkeypatch.setattr(
        sync_script,
        "sync_urlhaus",
        urlhaus_sync,
    )

    result = sync_script.main()

    assert result == 1
    phishing_sync.assert_not_called()
    urlhaus_sync.assert_called_once_with(failed_db)
    failed_db.close.assert_called_once()
    

def test_successful_sync_persists_history(monkeypatch):
    class FakeDB:
        def __init__(self):
            self.record = None

        def add(self, record):
            self.record = record

        def commit(self):
            pass

        def refresh(self, record):
            record.id = 1

        def close(self):
            pass

    db = FakeDB()

    monkeypatch.setattr(sync_script, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        sync_script,
        "sync_phishing_database",
        lambda session: {
            "source": "phishing_database",
            "downloaded": 100,
            "processed": 90,
            "skipped": 10,
            "batches": 2,
        },
    )

    monkeypatch.setattr(
        sync_script,
        "sync_urlhaus",
        lambda session: {
            "source": "urlhaus",
            "downloaded": 50,
            "processed": 45,
            "skipped": 5,
            "batches": 1,
        },
    )

    assert sync_script.main() == 0

    assert db.record.source == "urlhaus"
    assert db.record.status == "success"
    assert db.record.downloaded == 50
    assert db.record.processed == 45
    assert db.record.skipped == 5
    assert db.record.batches == 1
    assert db.record.completed_at is not None


def test_failed_sync_persists_failure_history(monkeypatch):
    class FakeDB:
        def __init__(self):
            self.record = None

        def add(self, record):
            self.record = record

        def commit(self):
            pass

        def refresh(self, record):
            record.id = 1

        def get(self, model, record_id):
            return self.record

        def rollback(self):
            pass

        def close(self):
            pass

    db = FakeDB()

    monkeypatch.setattr(sync_script, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        sync_script,
        "sync_phishing_database",
        lambda session: (_ for _ in ()).throw(
            RuntimeError("Feed unavailable")
        ),
    )
    monkeypatch.setattr(
        sync_script,
        "sync_urlhaus",
        lambda session: {
            "source": "urlhaus",
            "downloaded": 0,
            "processed": 0,
            "skipped": 0,
            "batches": 0,
        },
    )

    assert sync_script.main() == 1

    assert db.record.source == "urlhaus"
    assert db.record.status == "success"
    assert db.record.completed_at is not None



def test_failed_feed_records_error_and_continues(monkeypatch):
    class FakeDB:
        def __init__(self):
            self.record = None

        def add(self, record):
            self.record = record

        def commit(self):
            pass

        def refresh(self, record):
            record.id = 1

        def get(self, model, record_id):
            return self.record

        def rollback(self):
            pass

        def close(self):
            pass

    db_sessions = [FakeDB(), FakeDB()]
    session_factory = iter(db_sessions)

    monkeypatch.setattr(
        sync_script,
        "SessionLocal",
        lambda: next(session_factory),
    )

    def fail_phishing(session):
        raise RuntimeError("Feed unavailable")

    def succeed_urlhaus(session):
        return {
            "source": "urlhaus",
            "downloaded": 50,
            "processed": 45,
            "skipped": 5,
            "batches": 1,
        }

    monkeypatch.setattr(
        sync_script, "sync_phishing_database", fail_phishing
    )
    monkeypatch.setattr(
        sync_script, "sync_urlhaus", succeed_urlhaus
    )

    assert sync_script.main() == 1

    failed_record = db_sessions[0].record
    successful_record = db_sessions[1].record

    assert failed_record.source == "phishing_database"
    assert failed_record.status == "failed"
    assert failed_record.completed_at is not None
    assert "RuntimeError" in failed_record.error_message

    assert successful_record.source == "urlhaus"
    assert successful_record.status == "success"
    assert successful_record.processed == 45
