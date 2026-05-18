from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str


class EvaluationInput(BaseModel):
    model: str = Field(..., description="AI model identifier being called")
    messages: list[Message] = Field(..., min_length=1)
    metadata: dict = Field(default_factory=dict)


class EvaluationRequest(BaseModel):
    input: EvaluationInput


class EvaluationResponse(BaseModel):
    allowed: bool
    reason: str
    policy_version: str = "v1"
    evaluated_rules: list[str] = Field(default_factory=list)
