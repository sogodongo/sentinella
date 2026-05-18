import uuid
from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class CheckStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class CheckResult(BaseModel):
    check_name: str
    status: CheckStatus
    score: float = Field(ge=0.0, le=1.0)
    detail: str = ""


class EvaluationRequest(BaseModel):
    event_id: str
    model: str
    messages: list[dict]
    response: str | None = None
    metadata: dict = Field(default_factory=dict)


class EvaluationResult(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    model: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    overall_score: float = Field(ge=0.0, le=1.0)
    passed: bool
    checks: list[CheckResult]
