import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.bom import BOMDocument, ModelComponent
from app.services.generator import generate_bom, to_cyclonedx_json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["aibom"])

# In-memory store for development.
# Production: persist to MinIO and index in PostgreSQL.
_bom_store: dict[str, BOMDocument] = {}


@router.post("/bom", response_model=BOMDocument, status_code=201)
async def create_bom(component: ModelComponent) -> BOMDocument:
    """
    Generate and store a CycloneDX ML-BOM for a model component.
    Idempotent — re-submitting the same model_id overwrites the existing BOM.
    """
    doc = generate_bom(component)
    _bom_store[component.model_id] = doc

    logger.info(
        "BOM generated",
        extra={
            "model_id": component.model_id,
            "serial_number": doc.serial_number,
            "risk_level": component.eu_ai_act_risk_level,
        },
    )
    return doc


@router.get("/bom/{model_id}")
async def get_bom(model_id: str, format: str = "json") -> JSONResponse:
    """
    Retrieve a stored BOM by model ID.
    Supports ?format=cyclonedx for full CycloneDX 1.5 JSON export.
    """
    doc = _bom_store.get(model_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"no BOM found for model: {model_id}")

    if format == "cyclonedx":
        return JSONResponse(content=to_cyclonedx_json(doc))

    return JSONResponse(content=doc.model_dump(mode="json"))


@router.get("/bom")
async def list_boms() -> JSONResponse:
    """List all registered model BOMs."""
    return JSONResponse(content={
        "models": list(_bom_store.keys()),
        "total": len(_bom_store),
    })
