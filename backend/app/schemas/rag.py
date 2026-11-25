
from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=5)


class SourceResponse(BaseModel):
    source: str
    title: str | None = None
    source_urls: list[str] = Field(default_factory=list)
    similarity: float


class AssistantResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceResponse]
