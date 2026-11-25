
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    UniqueConstraint,
    Index,
)
from sqlalchemy.sql import func

from backend.app.database import Base


class ThreatIndicator(Base):
    __tablename__ = "threat_indicators"

    id = Column(Integer, primary_key=True, index=True)

    indicator = Column(Text, nullable=False)

    indicator_hash = Column(String(64), nullable=False)

    hostname = Column(String(255), nullable=False)

    threat_type = Column(String(50), nullable=False)

    source = Column(String(100), nullable=False)

    first_seen = Column(DateTime(timezone=True), nullable=True)

    last_seen = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "indicator_hash",
            "source",
            name="uq_threat_indicator_hash_source",
        ),
        Index("ix_threat_indicators_hostname", "hostname"),
        Index("ix_threat_indicators_source", "source"),
    )
