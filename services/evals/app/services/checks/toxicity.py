from app.config import settings
from app.models.evaluation import CheckResult, CheckStatus, EvaluationRequest
from app.services.checks.base import BaseCheck


class KeywordToxicityCheck(BaseCheck):
    """
    Keyword-based toxicity screen for input messages.

    This is a baseline check suitable for development and as a
    fast pre-filter. Production deployments should layer a
    proper classifier (e.g. OpenAI moderation API, Perspective API)
    on top of this.
    """

    @property
    def name(self) -> str:
        return "input.toxicity"

    def run(self, request: EvaluationRequest) -> CheckResult:
        combined = " ".join(
            m.get("content", "") for m in request.messages
        ).lower()

        hits = [kw for kw in settings.toxicity_keywords if kw in combined]

        if hits:
            score = max(0.0, 1.0 - len(hits) * 0.2)
            return CheckResult(
                check_name=self.name,
                status=CheckStatus.FAILED,
                score=round(score, 3),
                detail=f"flagged keywords detected: {', '.join(hits)}",
            )

        return CheckResult(
            check_name=self.name,
            status=CheckStatus.PASSED,
            score=1.0,
            detail="no flagged keywords detected",
        )
