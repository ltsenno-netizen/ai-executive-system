import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_intent(client):
    """Test GET /api/intent endpoint"""
    response = client.get("/api/intent")
    
    assert response.status_code == 200
    data = response.json()
    assert "growth_weight" in data
    assert "profitability_weight" in data
    assert "innovation_weight" in data
    assert "stability_weight" in data
    assert "risk_preference" in data
    assert "time_horizon" in data


def test_set_intent(client):
    """Test POST /api/intent/set endpoint"""
    response = client.post(
        "/api/intent/set",
        json={
            "growth_weight": 0.4,
            "profitability_weight": 0.2,
            "innovation_weight": 0.25,
            "stability_weight": 0.15,
            "risk_preference": 0.6,
            "time_horizon": 0.7,
            "cultural_identity": "innovative",
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert data["intent"]["growth_weight"] == 0.4
    assert data["intent"]["cultural_identity"] == "innovative"


def test_analyze_intent(client):
    """Test GET /api/intent/analysis endpoint"""
    # First set intent
    client.post(
        "/api/intent/set",
        json={
            "growth_weight": 0.35,
            "profitability_weight": 0.25,
            "innovation_weight": 0.25,
            "stability_weight": 0.15,
            "risk_preference": 0.6,
            "time_horizon": 0.7,
            "cultural_identity": "innovative",
        }
    )
    
    # Generate multi-objective data
    client.post("/api/multi-objective/run")
    
    # Analyze intent
    response = client.get("/api/intent/analysis")
    
    assert response.status_code == 200
    data = response.json()
    assert "current_intent" in data
    assert "frontier_score_distribution" in data


def test_get_optimal_strategy(client):
    """Test GET /api/intent/optimal-strategy endpoint"""
    # Set intent
    client.post(
        "/api/intent/set",
        json={
            "growth_weight": 0.35,
            "profitability_weight": 0.25,
            "innovation_weight": 0.25,
            "stability_weight": 0.15,
            "risk_preference": 0.6,
            "time_horizon": 0.7,
            "cultural_identity": "innovative",
        }
    )
    
    # Generate multi-objective data
    client.post("/api/multi-objective/run")
    
    # Get optimal strategy
    response = client.get("/api/intent/optimal-strategy")
    
    assert response.status_code == 200
    data = response.json()
    assert "strategy" in data
    assert "score" in data


def test_get_ranked_strategies(client):
    """Test GET /api/intent/ranked-strategies endpoint"""
    # Set intent
    client.post(
        "/api/intent/set",
        json={
            "growth_weight": 0.35,
            "profitability_weight": 0.25,
            "innovation_weight": 0.25,
            "stability_weight": 0.15,
            "risk_preference": 0.6,
            "time_horizon": 0.7,
            "cultural_identity": "innovative",
        }
    )
    
    # Generate multi-objective data
    client.post("/api/multi-objective/run")
    
    # Get ranked strategies
    response = client.get("/api/intent/ranked-strategies")
    
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "ranked_strategies" in data
    assert data["count"] > 0


def test_get_intent_markdown(client):
    """Test GET /api/intent/markdown endpoint"""
    response = client.get("/api/intent/markdown")
    
    assert response.status_code == 200
    data = response.json()
    assert "markdown" in data
    assert "企業意思" in data["markdown"]
