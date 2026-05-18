import logging

from fastapi import APIRouter

from app.models.evaluation import EvaluationRequest, EvaluationResult
from app.services.runner import run_evaluation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["evals"])


@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate(body: EvaluationRequest) -> EvaluationResult:
    """
    Run all registered evaluation checks against an inference event.
    Returns a scored result with per-check breakdown.
    """
    return run_evaluation(body)
