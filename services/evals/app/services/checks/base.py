from abc import ABC, abstractmethod

from app.models.evaluation import CheckResult, EvaluationRequest


class BaseCheck(ABC):
    """
    All evaluation checks implement this interface.
    Checks are stateless and synchronous — state lives in the runner.
    """

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def run(self, request: EvaluationRequest) -> CheckResult: ...
