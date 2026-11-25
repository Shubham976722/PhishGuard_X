
import logging
import sys
from datetime import datetime, timezone

from backend.app.database import SessionLocal
from backend.app.models.threat_feed_sync import ThreatFeedSync
from backend.app.services.threat_intel_service import sync_phishing_database
from backend.app.services.urlhaus_service import sync_urlhaus


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("phishguard.threat_feed_sync")


def main():
    feeds = [
        ("phishing_database", "Phishing.Database", sync_phishing_database),
        ("urlhaus", "URLhaus", sync_urlhaus),
    ]

    failures = []

    for source, feed_name, sync_function in feeds:
        db = None
        sync_run_id = None

        try:
            logger.info("Starting synchronization: %s", feed_name)

            db = SessionLocal()

            sync_run = ThreatFeedSync(
                source=source,
                status="running",
            )
            db.add(sync_run)
            db.commit()
            db.refresh(sync_run)

            sync_run_id = sync_run.id

            result = sync_function(db)

            sync_run.status = "success"
            sync_run.downloaded = result["downloaded"]
            sync_run.processed = result["processed"]
            sync_run.skipped = result["skipped"]
            sync_run.batches = result["batches"]
            sync_run.completed_at = datetime.now(timezone.utc)

            db.commit()

            logger.info(
                "Synchronization completed: %s | Results: %s",
                feed_name,
                result,
            )

        except Exception as exc:
            failures.append(feed_name)

            logger.exception(
                "Synchronization failed: %s",
                feed_name,
            )

            if db is not None and sync_run_id is not None:
                try:
                    db.rollback()

                    failed_run = db.get(ThreatFeedSync, sync_run_id)

                    if failed_run is not None:
                        failed_run.status = "failed"
                        failed_run.completed_at = datetime.now(timezone.utc)
                        failed_run.error_message = (
                            f"{type(exc).__name__}: "
                            "Synchronization failed. See application logs."
                        )
                        db.commit()

                except Exception:
                    db.rollback()
                    logger.exception(
                        "Unable to update synchronization history: %s",
                        feed_name,
                    )

        finally:
            if db is not None:
                db.close()

    if failures:
        logger.error(
            "Threat-feed synchronization finished with failures: %s",
            ", ".join(failures),
        )
        return 1

    logger.info("All threat-feed synchronizations completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
