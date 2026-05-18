import logging

from app.models.evaluation import EvaluationRequest, EvaluationResult
from app.services.checks.length import ResponseLengthCheck
from app.services.checks.toxicity import KeywordToxicityCheck

logger = logging.getLogger(__name__)

# Register all active checks here.
# Order matters — checks run sequentially and all results are collected.
_CHECKS = [
    KeywordToxicityCheck(),
    ResponseLengthCheck(),
]


def run_evaluation(request: EvaluationRequest) -> EvaluationResult:
    results = [check.run(request) for check in _CHECKS]

    passed_checks = [r for r in results if r.status == "passed"]
    scored_checks = [r for r in results if r.status != "skipped"]

    overall_score = (
        sum(r.score for r in scored_checks) / len(scored_checks)
        if scored_checks else 1.0
    )
    passed = all(r.status != "failed" for r in results)

    logger.info(
        "evaluation complete",
        extra={
            "event_id": request.event_id,
            "model": request.model,
            "passed": passed,
            "score": round(overall_score, 3),
            "checks_run": len(results),
            "checks_passed": len(passed_checks),
        },
    )

    return EvaluationResult(
        event_id=request.event_id,
        model=request.model,
        overall_score=round(overall_score, 3),
        passed=passed,
        checks=results,
    )
