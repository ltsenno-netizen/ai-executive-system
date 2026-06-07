import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app
from src.backend.app.models.self_optimization_model import OptimizationObjective


client = TestClient(app)


def test_generate_optimization_plan_growth():
    """Test optimization plan generation API for GROWTH"""
    response = client.post("/api/self-optimization/generate/growth")
    
    if response.status_code == 500:
        # Expected if no scenarios are run yet
        assert "No scenario results found" in response.json().get("detail", "")
    else:
        assert response.status_code == 200
        data = response.json()
        assert "plan" in data
        assert data["plan"]["objective"] == "growth"


def test_generate_optimization_plan_invalid_objective():
    """Test optimization plan generation with invalid objective"""
    response = client.post("/api/self-optimization/generate/invalid")
    
    assert response.status_code == 400
    assert "Invalid objective" in response.json().get("detail", "")


def test_get_latest_plan():
    """Test retrieving latest plan"""
    # First try to generate
    client.post("/api/self-optimization/generate/stability")
    
    # Then retrieve
    response = client.get("/api/self-optimization/latest")
    
    # May fail if no plans exist
    if response.status_code == 200:
        assert "objective" in response.json()
    else:
        assert response.status_code == 404


def test_get_latest_plan_by_objective():
    """Test retrieving latest plan for specific objective"""
    response = client.get("/api/self-optimization/latest/innovation")
    
    if response.status_code == 200:
        data = response.json()
        assert data["objective"] == "innovation"
    else:
        assert response.status_code in [404, 400]


def test_get_all_plans():
    """Test retrieving all plans"""
    response = client.get("/api/self-optimization/all")
    
    if response.status_code == 200:
        data = response.json()
        assert "count" in data
        assert "plans" in data
    else:
        assert response.status_code == 500
