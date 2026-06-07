from fastapi.testclient import TestClient

from src.backend.app.main import app

client = TestClient(app)


def test_executive_simulation_api_endpoints():
    payload = {
        "scenario_type": "baseline",
        "focus_horizon": "MID",
    }

    run_response = client.post("/api/executive-simulation/run", json=payload)
    assert run_response.status_code == 200
    data = run_response.json()
    assert data.get("simulation_id")
    assert data.get("scenario_type") == "baseline"
    assert "ceo_summary" in data

    latest_response = client.get("/api/executive-simulation/latest")
    assert latest_response.status_code == 200
    latest_data = latest_response.json()
    assert latest_data.get("simulation_id") == data.get("simulation_id")

    history_response = client.get("/api/executive-simulation/history")
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert isinstance(history_data, list)
    assert any(item.get("simulation_id") == data.get("simulation_id") for item in history_data)

    simulation_id = data.get("simulation_id")
    item_response = client.get(f"/api/executive-simulation/{simulation_id}")
    assert item_response.status_code == 200
    assert item_response.json().get("simulation_id") == simulation_id

    markdown_response = client.get(f"/api/executive-simulation/{simulation_id}/markdown")
    assert markdown_response.status_code == 200
    assert "content" in markdown_response.json()
