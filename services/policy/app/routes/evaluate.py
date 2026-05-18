import logging

from fastapi import APIRouter, HTTPException

from app.models.policy import EvaluationRequest, EvaluationResponse
from app.services import opa

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["policy"])


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_request(body: EvaluationRequest) -> EvaluationResponse:
    """
    Evaluate an AI inference request against active governance policies.

    The gateway calls this endpoint synchronously on every inference request.
    Response time directly affects user-facing latency — OPA evaluation
    must complete within the configured timeout.
    """
    input_doc = {
        "model": body.input.model,
        "messages": [m.model_dump() for m in body.input.messages],
        "metadata": body.input.metadata,
    }

    try:
        result = await opa.evaluate(input_doc)
    except Exception as exc:
        logger.exception("unexpected error during policy evaluation")
        raise HTTPException(status_code=500, detail="policy evaluation failed") from exc

    return EvaluationResponse(
        allowed=result["allowed"],
        reason=result["reason"],
        evaluated_rules=result.get("evaluated_rules", []),
    )
