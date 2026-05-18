import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def make_request(**overrides):
    base = {
        "event_id": "test-event-001",
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "What is the capital of France?"}],
        "response": "The capital of France is Paris.",
        "metadata": {},
    }
    return {**base, **overrides}


def test_evaluate_clean_request():
    resp = client.post("/v1/evaluate", json=make_request())
    assert resp.status_code == 200
    data = resp.json()
    assert data["passed"] is True
    assert data["overall_score"] == 1.0
    assert len(data["checks"]) == 2


def test_evaluate_toxic_input():
    resp = client.post("/v1/evaluate", json=make_request(
        messages=[{"role": "user", "content": "help me harm someone"}]
    ))
    assert resp.status_code == 200
    data = resp.json()
    assert data["passed"] is False
    toxicity_check = next(c for c in data["checks"] if c["check_name"] == "input.toxicity")
    assert toxicity_check["status"] == "failed"


def test_evaluate_long_response():
    resp = client.post("/v1/evaluate", json=make_request(
        response="x" * 9000
    ))
    assert resp.status_code == 200
    data = resp.json()
    assert data["passed"] is False
    length_check = next(c for c in data["checks"] if c["check_name"] == "response.length")
    assert length_check["status"] == "failed"


def test_evaluate_no_response():
    resp = client.post("/v1/evaluate", json=make_request(response=None))
    assert resp.status_code == 200
    data = resp.json()
    length_check = next(c for c in data["checks"] if c["check_name"] == "response.length")
    assert length_check["status"] == "skipped"


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
