from typing import Literal

from pydantic import BaseModel, Field


class CheckRequest(BaseModel):
    source_context: str = Field(..., min_length=1, max_length=20_000)
    agent_output: str = Field(..., min_length=1, max_length=20_000)


class ClaimVerdict(BaseModel):
    claim: str
    status: Literal["PASS", "FLAGGED"]
    severity: Literal["none", "low", "medium", "high"]
    confidence: float = Field(..., ge=0, le=1)
    explanation: str
    source_quote: str | None = None


class CheckResult(BaseModel):
    verdicts: list[ClaimVerdict]
    summary: str


class CheckResponse(CheckResult):
    model: str
