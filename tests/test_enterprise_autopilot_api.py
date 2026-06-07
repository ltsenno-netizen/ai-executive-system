from fastapi.testclient import TestClient

from src.backend.app.main import app

client = TestClient(app)


def test_autopilot_run_endpoint():
    response = client.post("/api/enterprise-autopilot/run")
    assert response.status_code == 200
    data = response.json()
    assert data.get("cycle_id") is not None
    assert data.get("overall_status") in {"COMPLETED", "FAILED"}


def test_autopilot_latest_endpoint():
    response = client.get("/api/enterprise-autopilot/latest")
    assert response.status_code == 200
    data = response.json()
    assert data.get("cycle_id") is not None
