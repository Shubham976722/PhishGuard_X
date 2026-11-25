from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.sql import func

from backend.app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    url = Column(Text, nullable=False)

    risk_score = Column(Float, nullable=True)

    risk_level = Column(String(20), nullable=True)

    verdict = Column(
        String(30),
        nullable=False,
        default="pending"
    )

    threat_type = Column(String(100), nullable=True)

    match_type = Column(String(30), nullable=True)

    threat_sources = Column(
        JSON,
        nullable=False,
        default=list
    )

    threat_types = Column(
        JSON,
        nullable=False,
        default=list
    )

    explanation = Column(Text, nullable=True)

    scanned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
