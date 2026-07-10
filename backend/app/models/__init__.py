from pydantic import BaseModel, Field
from datetime import datetime


class SourceDocument(BaseModel):
    source_name: str
    url: str | None = None
    raw_text: str
    fetched_at: datetime = Field(default_factory=datetime.now)


class ExtractionResult(BaseModel):
    company_name: str
    description: str
    funding_stage: str | None = None
    funding_mentions: list[str] = Field(default_factory=list)
    founder_mentions: list[str] = Field(default_factory=list)
    market_signals: list[str] = Field(default_factory=list)


class Snapshot(BaseModel):
    company_name: str
    summary: str
    market_signal: str
    funding_stage: str | None = None
    founder_background: str
    risk_flags: list[str]