import logging

from fastapi import APIRouter, Query, Request

from app.config import settings
from app.models.event import EventListResponse, InferenceEvent, PolicyDecision
from app.services import store, stream

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["ledger"])


@router.post("/events", response_model=InferenceEvent, status_code=201)
async def record_event(body: InferenceEvent, request: Request) -> InferenceEvent:
    """
    Record an AI inference event to the audit ledger.
    Called by the gateway after every policy decision.
    Write is fire-and-forget to Kafka; PostgreSQL is the durable store.
    """
    if not body.caller_ip:
        body.caller_ip = request.client.host if request.client else None

    await store.write_event(body)
    await stream.publish_event(body)

    logger.info(
        "inference event recorded",
        extra={
            "event_id": body.event_id,
            "model": body.model,
            "decision": body.policy_decision,
        },
    )
    return body


@router.get("/events", response_model=EventListResponse)
async def list_events(
    limit: int = Query(default=50, le=settings.events_page_size),
    offset: int = Query(default=0, ge=0),
) -> EventListResponse:
    """
    List audit events in reverse chronological order.
    Used by the console for compliance dashboards.
    """
    events, total = await store.list_events(limit=limit, offset=offset)
    return EventListResponse(
        events=[InferenceEvent(**e) for e in events],
        total=total,
        page_size=limit,
    )
