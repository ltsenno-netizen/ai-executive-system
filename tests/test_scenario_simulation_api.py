from fastapi.testclient import TestClient
from src.backend.app.main import app
from src.backend.app.models.scenario_model import ScenarioType

client = TestClient(app)


def test_run_scenario_simulations_endpoint():
    response = client.post("/api/scenario-simulations/run")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "results" in data
    assert len(data["results"]) == 5

    for result in data["results"]:
        assert "scenario_type" in result
        assert "projected_environment" in result
        assert "projected_culture" in result
        assert "projected_consciousness_evolution" in result
        assert "financial_impact_summary" in result
        assert "risk_assessment" in result
        assert "opportunity_assessment" in result


def test_get_latest_scenario_simulations_endpoint():
    client.post("/api/scenario-simulations/run")
    response = client.get("/api/scenario-simulations/latest")

    assert response.status_code == 200
    data = response.json()
    assert "simulations" in data
    assert len(data["simulations"]) >= 5


def test_get_scenario_simulation_by_type_endpoint():
    client.post("/api/scenario-simulations/run")
    for scenario_type in ScenarioType:
        response = client.get(f"/api/scenario-simulations/{scenario_type.value}")
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_type"] == scenario_type.value
        assert "projected_environment" in data
        assert "projected_culture" in data
        assert "projected_consciousness_evolution" in data


def test_get_scenario_simulation_preview_endpoint():
    client.post("/api/scenario-simulations/run")
    response = client.get("/api/scenario-simulations/preview")
    assert response.status_code == 200
    data = response.json()
    assert "scenario_type" in data
    assert "risk_assessment" in data
    assert "opportunity_assessment" in data
    assert "confidence" in data
