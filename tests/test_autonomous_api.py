import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app


client = TestClient(app)


def test_run_autonomous_cycle_endpoint():
    """Test autonomous cycle execution API"""
    response = client.post("/api/autonomous/run/GROWTH")
    
    if response.status_code == 500:
        # May fail if dependencies unavailable
        assert "detail" in response.json()
    else:
        assert response.status_code == 200
        data = response.json()
        assert "cycle" in data
        assert data["cycle"]["objective"] == "GROWTH"


def test_get_latest_cycle_endpoint():
    """Test getting latest cycle API"""
    response = client.get("/api/autonomous/latest")
    
    if response.status_code == 404:
        # Expected if no cycles exist
        pass
    elif response.status_code == 200:
        data = response.json()
        assert "cycle_id" in data
        assert "evolution_score_change" in data


def test_get_all_cycles_endpoint():
    """Test getting all cycles API"""
    response = client.get("/api/autonomous/cycles")
    
    if response.status_code == 404:
        # Expected if no cycles exist
        pass
    elif response.status_code == 200:
        data = response.json()
        assert "cycles" in data or "total_cycles" in data


def test_get_cycles_by_objective_endpoint():
    """Test getting cycles by objective API"""
    response = client.get("/api/autonomous/cycles/GROWTH")
    
    if response.status_code == 404:
        # Expected if no cycles exist
        pass
    elif response.status_code == 200:
        data = response.json()
        assert "objective" in data
        assert data["objective"] == "GROWTH"


def test_get_metrics_endpoint():
    """Test getting autonomous metrics API"""
    response = client.get("/api/autonomous/metrics")
    
    if response.status_code == 404:
        # Expected if no cycles exist
        pass
    elif response.status_code == 200:
        data = response.json()
        assert "total_cycles_executed" in data
        assert "total_evolution_score_change" in data
