import uuid
from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class PolicyDecision(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    BYPASSED = "bypassed"  # policy service unavailable, fail-open applied


class InferenceEvent(BaseModel):
    """
    Canonical audit record for a single AI inference request.
    Immutable once written — no update path exists by design.
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model: str
    policy_decision: PolicyDecision
    policy_reason: str
    caller_ip: str | None = None
    request_message_count: int
    metadata: dict = Field(default_factory=dict)


class EventListResponse(BaseModel):
    events: list[InferenceEvent]
    total: int
    page_size: int
