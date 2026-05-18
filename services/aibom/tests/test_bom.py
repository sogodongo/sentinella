import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.bom import _bom_store

client = TestClient(app)


def make_component(**overrides):
    base = {
        "model_id": "gpt-4o",
        "name": "GPT-4o",
        "version": "2024-05-13",
        "model_type": "llm",
        "supplier": {"name": "OpenAI", "url": "https://openai.com"},
        "description": "Multimodal large language model",
        "intended_use": "General purpose text generation",
        "eu_ai_act_risk_level": "limited",
        "licenses": ["proprietary"],
    }
    return {**base, **overrides}


def setup_function():
    _bom_store.clear()


def test_create_bom():
    resp = client.post("/v1/bom", json=make_component())
    assert resp.status_code == 201
    data = resp.json()
    assert data["component"]["model_id"] == "gpt-4o"
    assert "serial_number" in data
    assert data["bom_version"] == "1.5"


def test_get_bom():
    client.post("/v1/bom", json=make_component())
    resp = client.get("/v1/bom/gpt-4o")
    assert resp.status_code == 200
    assert resp.json()["component"]["name"] == "GPT-4o"


def test_get_bom_cyclonedx_format():
    client.post("/v1/bom", json=make_component())
    resp = client.get("/v1/bom/gpt-4o?format=cyclonedx")
    assert resp.status_code == 200
    data = resp.json()
    assert data["bomFormat"] == "CycloneDX"
    assert data["specVersion"] == "1.5"
    assert data["components"][0]["type"] == "machine-learning-model"


def test_get_bom_not_found():
    resp = client.get("/v1/bom/nonexistent-model")
    assert resp.status_code == 404


def test_list_boms():
    resp = client.get("/v1/bom")
    assert resp.status_code == 200
    assert "models" in resp.json()


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
