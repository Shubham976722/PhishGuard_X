from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict, Field


class ScanRequest(BaseModel):
    url: HttpUrl = Field(
        ...,
        max_length=2048,
        description="Target URL to analyze (HTTP or HTTPS, max 2048 chars)"
    )


class ScanResponse(BaseModel):
    id: int
    user_id: int | None
    url: str
    risk_score: float | None
    risk_level: str | None
    verdict: str
    threat_type: str | None
    match_type: str | None
    threat_sources: list[str]
    threat_types: list[str]
    explanation: str | None
    scanned_at: datetime

    model_config = ConfigDict(from_attributes=True)
