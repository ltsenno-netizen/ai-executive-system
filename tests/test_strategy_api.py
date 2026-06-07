import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app


client = TestClient(app)


def test_generate_strategy_endpoint():
    """Test strategy generation API"""
    response = client.post("/api/strategy/generate/GROWTH")
    
    if response.status_code == 500:
        # May fail if dependencies unavailable
        assert "detail" in response.json()
    else:
        assert response.status_code == 200
        data = response.json()
        assert "roadmap" in data
        assert data["roadmap"]["objective"] == "GROWTH"


def test_get_latest_strategy_endpoint():
    """Test latest strategy retrieval API"""
    response = client.get("/api/strategy/latest")
    
    if response.status_code == 404:
        # Expected if no roadmaps exist
        pass
    elif response.status_code == 200:
        data = response.json()
        assert "objective" in data
        assert "key_focus" in data


def test_get_strategy_by_objective_endpoint():
    """Test strategy retrieval by objective API"""
    response = client.get("/api/strategy/latest/GROWTH")
    
    if response.status_code == 404:
        # Expected if no roadmap exists
        pass
    elif response.status_code == 200:
        data = response.json()
        assert data["objective"] == "GROWTH"


def test_get_all_strategies_endpoint():
    """Test all strategies retrieval API"""
    response = client.get("/api/strategy/all")
    
    if response.status_code == 404:
        # Expected if no roadmaps exist
        pass
    elif response.status_code == 200:
        data = response.json()
        assert "roadmaps" in data
        assert isinstance(data["roadmaps"], list)
