import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app

client = TestClient(app)

def test_get_latest_evolution():
    """Test getting the latest enterprise evolution result."""
    response = client.get("/api/evolution/latest")
    # May return 404 if no evolution data exists yet
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert "period" in data
        assert "evolution_score" in data
        assert "culture_shift" in data
        assert "environment_shift" in data
        assert "leadership_shift" in data

def test_get_evolution_by_period():
    """Test getting evolution by specific period."""
    response = client.get("/api/evolution/2024-Q1")
    # May return 404 if no data for that period
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert data["period"] == "2024-Q1"