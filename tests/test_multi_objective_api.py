import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_run_multi_objective_analysis(client):
    """Test POST /api/multi-objective/run endpoint"""
    response = client.post("/api/multi-objective/run")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "frontier" in data
    assert data["frontier"]["frontier_count"] > 0


def test_get_frontier(client):
    """Test GET /api/multi-objective/frontier endpoint"""
    # Run analysis first
    client.post("/api/multi-objective/run")
    
    # Get frontier
    response = client.get("/api/multi-objective/frontier")
    
    assert response.status_code == 200
    data = response.json()
    assert "frontier_count" in data
    assert "candidates" in data


def test_get_all_candidates(client):
    """Test GET /api/multi-objective/candidates endpoint"""
    # Run analysis first
    client.post("/api/multi-objective/run")
    
    # Get candidates
    response = client.get("/api/multi-objective/candidates")
    
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "candidates" in data
    assert data["count"] > 0


def test_get_frontier_candidates(client):
    """Test GET /api/multi-objective/frontier-candidates endpoint"""
    # Run analysis first
    client.post("/api/multi-objective/run")
    
    # Get frontier candidates
    response = client.get("/api/multi-objective/frontier-candidates")
    
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "frontier_candidates" in data
    assert data["count"] > 0


def test_get_frontier_no_data(client):
    """Test frontier endpoint with no data returns 404"""
    # Try to get frontier without running analysis first
    import os
    frontier_path = "data/multi_objective/frontier.json"
    if os.path.exists(frontier_path):
        os.remove(frontier_path)
    
    response = client.get("/api/multi-objective/frontier")
    
    assert response.status_code == 404
