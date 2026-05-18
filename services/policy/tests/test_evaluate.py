import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app

client = TestClient(app)


def make_request(model="gpt-4o", content="Hello"):
    return {
        "input": {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "metadata": {},
        }
    }


@patch("app.routes.evaluate.opa.evaluate", new_callable=AsyncMock)
def test_evaluate_allowed(mock_opa):
    mock_opa.return_value = {
        "allowed": True,
        "reason": "policy_passed",
        "evaluated_rules": ["inference.model_allowed"],
    }

    resp = client.post("/v1/evaluate", json=make_request())
    assert resp.status_code == 200
    data = resp.json()
    assert data["allowed"] is True
    assert data["reason"] == "policy_passed"


@patch("app.routes.evaluate.opa.evaluate", new_callable=AsyncMock)
def test_evaluate_denied(mock_opa):
    mock_opa.return_value = {
        "allowed": False,
        "reason": "model_not_permitted",
        "evaluated_rules": ["inference.model_allowed"],
    }

    resp = client.post("/v1/evaluate", json=make_request(model="restricted-model"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["allowed"] is False
    assert data["reason"] == "model_not_permitted"


def test_evaluate_missing_messages():
    resp = client.post("/v1/evaluate", json={"input": {"model": "gpt-4o", "messages": []}})
    assert resp.status_code == 422


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
