import json
import uuid
from datetime import timezone

from app.models.bom import BOMDocument, ModelComponent


def generate_bom(component: ModelComponent) -> BOMDocument:
    """
    Build a CycloneDX-aligned ML-BOM document for the given model component.

    The output structure follows CycloneDX 1.5 JSON schema with Sentinella
    extensions for EU AI Act risk classification and governance metadata.
    Full CycloneDX serialisation via cyclonedx-python-lib is available
    for export endpoints — this generates the internal representation.
    """
    return BOMDocument(
        serial_number=f"urn:uuid:{uuid.uuid4()}",
        component=component,
    )


def to_cyclonedx_json(doc: BOMDocument) -> dict:
    """
    Serialise a BOMDocument to CycloneDX 1.5 JSON format.
    This is the format exported to MinIO and returned by the API.
    """
    component = doc.component

    return {
        "bomFormat": "CycloneDX",
        "specVersion": doc.bom_version,
        "serialNumber": doc.serial_number,
        "version": 1,
        "metadata": {
            "timestamp": doc.generated_at.astimezone(timezone.utc).isoformat(),
            "tools": [
                {
                    "vendor": "Sentinella",
                    "name": "sentinella-aibom",
                    "version": "0.1.0",
                }
            ],
        },
        "components": [
            {
                "type": "machine-learning-model",
                "bom-ref": component.model_id,
                "name": component.name,
                "version": component.version,
                "description": component.description,
                "supplier": {
                    "name": component.supplier.name,
                    "url": [component.supplier.url] if component.supplier.url else [],
                },
                "licenses": [{"license": {"name": lic}} for lic in component.licenses],
                "modelCard": {
                    "modelParameters": {
                        "task": component.model_type.value,
                        "architectureFamily": component.model_type.value,
                    },
                    "considerations": {
                        "users": [component.intended_use] if component.intended_use else [],
                        "technicalLimitations": [component.limitations] if component.limitations else [],
                        "trainingData": [
                            {"name": component.training_data_description}
                        ] if component.training_data_description else [],
                    },
                },
                "properties": [
                    {
                        "name": "sentinella:eu_ai_act_risk_level",
                        "value": component.eu_ai_act_risk_level.value,
                    },
                    {
                        "name": "sentinella:schema_version",
                        "value": doc.sentinella_schema_version,
                    },
                    *[
                        {"name": f"sentinella:{k}", "value": str(v)}
                        for k, v in component.properties.items()
                    ],
                ],
            }
        ],
    }
