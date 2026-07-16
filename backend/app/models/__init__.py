from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class SourceDocument(BaseModel):
    """
    Raw text pulled from a single source during ingestion.
    This is the output of the ingestion layer and the input to extraction.
    """
    source_name: str
    url: str | None = None
    raw_text: str
    fetched_at: datetime = Field(default_factory=datetime.now)


class ExtractionResult(BaseModel):
    """
    Structured facts pulled from raw source text by the extraction layer.
    This is intentionally "raw findings," not polished prose — funding_mentions,
    founder_mentions, and market_signals are lists of facts, not written
    narrative.
    """

    company_name: str = Field(
        description="The company's real, properly capitalized official name, "
                    "as it appears in the source text — not necessarily matching "
                    "the input query's casing or wording."
    )
    description: str
    funding_stage: str | None = None
    funding_mentions: list[str] = Field(default_factory=list)
    founder_mentions: list[str] = Field(default_factory=list)
    market_signals: list[str] = Field(default_factory=list)


class Snapshot(BaseModel):
    """
    Final, polished due diligence snapshot returned to the frontend.
    This is the output of the synthesis layer — the only place in the
    pipeline where prose and judgment calls (like risk_flags) get written.
    """
    company_name: str
    summary: str
    market_signal: str
    funding_stage: str | None = None
    founder_background: str
    risk_flags: list[str]


class SnapshotRequest(BaseModel):

    """ Request body for POST /api/snapshot """
    query: str = Field(min_length=1)

    @field_validator("query")
    @classmethod
    def strip_and_validate(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("query cannot be empty or whitespace")
        return stripped
