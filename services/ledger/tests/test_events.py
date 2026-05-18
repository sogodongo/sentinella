from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def make_event(**overrides):
    base = {
        "model": "gpt-4o",
        "policy_decision": "allowed",
        "policy_reason": "policy_passed",
        "request_message_count": 2,
        "metadata": {},
    }
    return {**base, **overrides}


@patch("app.routes.events.store.write_event", new_callable=AsyncMock)
@patch("app.routes.events.stream.publish_event", new_callable=AsyncMock)
def test_record_event(mock_stream, mock_store):
    resp = client.post("/v1/events", json=make_event())
    assert resp.status_code == 201
    data = resp.json()
    assert data["model"] == "gpt-4o"
    assert data["policy_decision"] == "allowed"
    assert "event_id" in data
    assert "timestamp" in data
    mock_store.assert_awaited_once()
    mock_stream.assert_awaited_once()


@patch("app.routes.events.store.write_event", new_callable=AsyncMock)
@patch("app.routes.events.stream.publish_event", new_callable=AsyncMock)
def test_record_denied_event(mock_stream, mock_store):
    resp = client.post("/v1/events", json=make_event(
        policy_decision="denied",
        policy_reason="model_not_permitted",
    ))
    assert resp.status_code == 201
    assert resp.json()["policy_decision"] == "denied"


@patch("app.routes.events.store.list_events", new_callable=AsyncMock)
def test_list_events(mock_list):
    mock_list.return_value = ([], 0)
    resp = client.get("/v1/events")
    assert resp.status_code == 200
    data = resp.json()
    assert "events" in data
    assert data["total"] == 0


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
