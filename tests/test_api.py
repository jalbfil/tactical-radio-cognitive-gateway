from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    payload = response.json()
    assert "classification" in payload
    assert "decision" in payload


def test_set_jammed_scenario():
    response = client.post("/api/scenario/jammed_attack")
    assert response.status_code == 200
    payload = response.json()
    assert payload["scenario"] == "jammed_attack"
    assert payload["classification"]["state"] == "JAMMED_ATTACK"


def test_history_endpoint_after_tick():
    response = client.post("/api/tick")
    assert response.status_code == 200

    history = client.get("/api/history")
    assert history.status_code == 200
    payload = history.json()
    assert "history" in payload
    assert len(payload["history"]) >= 1


def test_export_report_endpoint():
    response = client.get("/api/export-report")
    assert response.status_code == 200
    payload = response.json()
    assert payload["report_type"] == "tactical-radio-cognitive-gateway"
    assert "classification" in payload
    assert "gateway_decision" in payload
    assert "metrics" in payload


def test_playback_endpoint():
    response = client.post("/api/playback")
    assert response.status_code == 200
    payload = response.json()
    assert "sequence" in payload
    assert "history" in payload
    assert len(payload["sequence"]) == 3
    assert payload["sequence"][-1]["classification"]["state"] == "JAMMED_ATTACK"
