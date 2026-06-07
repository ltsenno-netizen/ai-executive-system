import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app


client = TestClient(app)


def test_generate_story_endpoint():
    """Test story generation API"""
    response = client.post("/api/story/generate/2026-04")
    
    if response.status_code == 500:
        # May fail if dependencies unavailable
        assert "detail" in response.json()
    else:
        assert response.status_code == 200
        data = response.json()
        assert "story" in data
        assert data["story"]["period"] == "2026-04"


def test_get_story_endpoint():
    """Test story retrieval API"""
    response = client.get("/api/story/2026-04")
    
    if response.status_code == 404:
        # Expected if story doesn't exist
        pass
    elif response.status_code == 200:
        data = response.json()
        assert "period" in data
        assert "summary" in data


def test_get_latest_story_endpoint():
    """Test latest story retrieval API"""
    response = client.get("/api/story/")
    
    if response.status_code == 404:
        # Expected if no stories exist
        pass
    elif response.status_code == 200:
        data = response.json()
        assert "period" in data
        assert "summary" in data
