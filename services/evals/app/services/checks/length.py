from app.config import settings
from app.models.evaluation import CheckResult, CheckStatus, EvaluationRequest
from app.services.checks.base import BaseCheck


class ResponseLengthCheck(BaseCheck):
    """
    Flags responses that exceed the configured maximum length.
    Abnormally long responses can indicate prompt injection or
    data exfiltration attempts.
    """

    @property
    def name(self) -> str:
        return "response.length"

    def run(self, request: EvaluationRequest) -> CheckResult:
        if not request.response:
            return CheckResult(
                check_name=self.name,
                status=CheckStatus.SKIPPED,
                score=1.0,
                detail="no response to evaluate",
            )

        length = len(request.response)
        max_len = settings.max_response_length

        if length > max_len:
            score = max(0.0, 1.0 - (length - max_len) / max_len)
            return CheckResult(
                check_name=self.name,
                status=CheckStatus.FAILED,
                score=round(score, 3),
                detail=f"response length {length} exceeds maximum {max_len}",
            )

        return CheckResult(
            check_name=self.name,
            status=CheckStatus.PASSED,
            score=1.0,
            detail=f"response length {length} within bounds",
        )
