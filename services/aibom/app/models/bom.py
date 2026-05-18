from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class ModelType(StrEnum):
    LLM = "llm"
    CLASSIFIER = "classifier"
    EMBEDDING = "embedding"
    DIFFUSION = "diffusion"
    OTHER = "other"


class RiskLevel(StrEnum):
    MINIMAL = "minimal"
    LIMITED = "limited"
    HIGH = "high"
    UNACCEPTABLE = "unacceptable"


class ModelSupplier(BaseModel):
    name: str
    url: str | None = None
    contact: str | None = None


class ModelComponent(BaseModel):
    """
    Describes a single AI model component for inclusion in the ML-BOM.
    Maps to CycloneDX component type 'machine-learning-model'.
    """
    model_id: str = Field(..., description="Unique identifier, e.g. openai/gpt-4o")
    name: str
    version: str
    model_type: ModelType
    supplier: ModelSupplier
    description: str = ""
    intended_use: str = ""
    limitations: str = ""
    training_data_description: str = ""
    eu_ai_act_risk_level: RiskLevel = RiskLevel.LIMITED
    licenses: list[str] = Field(default_factory=list)
    properties: dict = Field(default_factory=dict)


class BOMDocument(BaseModel):
    bom_version: str = "1.5"
    serial_number: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    component: ModelComponent
    sentinella_schema_version: str = "v1"
