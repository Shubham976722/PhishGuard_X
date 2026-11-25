from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from backend.app.database import Base


class ThreatFeedSync(Base):
    __tablename__ = "threat_feed_syncs"

    id = Column(Integer, primary_key=True, index=True)

    source = Column(String(100), nullable=False)

    status = Column(String(20), nullable=False)

    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    completed_at = Column(DateTime(timezone=True), nullable=True)

    downloaded = Column(Integer, nullable=False, server_default="0")

    processed = Column(Integer, nullable=False, server_default="0")

    skipped = Column(Integer, nullable=False, server_default="0")

    batches = Column(Integer, nullable=False, server_default="0")

    error_message = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'success', 'failed')",
            name="ck_threat_feed_sync_status",
        ),
        Index(
            "ix_threat_feed_syncs_source_started_at",
            "source",
            "started_at",
        ),
    )

