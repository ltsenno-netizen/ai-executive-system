from fastapi.testclient import TestClient
from src.backend.app.main import app


client = TestClient(app)


def test_strategy_engine_v2_api_run_and_retrieve():
    response = client.post("/api/strategy/v2/run/baseline")
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_type"] == "baseline"
    assert "alignment_score" in data

    response_latest = client.get("/api/strategy/v2/latest/baseline")
    assert response_latest.status_code == 200
    latest_data = response_latest.json()
    assert latest_data["scenario_type"] == "baseline"

    response_markdown = client.get("/api/strategy/v2/markdown/baseline")
    assert response_markdown.status_code == 200
    assert "markdown" in response_markdown.json()
