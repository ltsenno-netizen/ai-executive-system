"""
Multi-Company Comparative API Tests (Step AK)
"""

from fastapi.testclient import TestClient
from src.backend.app.main import app

client = TestClient(app)


def test_list_available_companies():
    """Test GET /api/companies endpoint."""
    response = client.get("/api/companies")
    assert response.status_code == 200
    data = response.json()
    assert "companies" in data
    assert "count" in data
    assert data["count"] > 0


def test_compare_companies():
    """Test POST /api/companies/compare endpoint."""
    response = client.post(
        "/api/companies/compare",
        json=[
            {"company_id": "self", "name": "Our Company"},
            {"company_id": "competitor_a", "name": "Competitor A"},
        ]
    )
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert "companies" in data
    assert "metrics" in data
    assert "clusters" in data
    assert "narrative_summary" in data


def test_get_latest_comparison():
    """Test GET /api/companies/compare/latest endpoint."""
    # First, generate a comparison
    client.post(
        "/api/companies/compare",
        json=[
            {"company_id": "a", "name": "A"},
            {"company_id": "b", "name": "B"},
        ]
    )
    
    # Then retrieve it
    response = client.get("/api/companies/compare/latest")
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert "companies" in data


def test_get_comparison_report():
    """Test GET /api/companies/compare/{report_id} endpoint."""
    # Generate comparison
    gen_response = client.post(
        "/api/companies/compare",
        json=[
            {"company_id": "a", "name": "A"},
            {"company_id": "b", "name": "B"},
        ]
    )
    report_id = gen_response.json()["report_id"]
    
    # Retrieve specific report
    response = client.get(f"/api/companies/compare/{report_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] == report_id


def test_get_comparison_markdown():
    """Test GET /api/companies/compare/{report_id}/markdown endpoint."""
    # Generate comparison
    gen_response = client.post(
        "/api/companies/compare",
        json=[
            {"company_id": "a", "name": "A"},
            {"company_id": "b", "name": "B"},
        ]
    )
    report_id = gen_response.json()["report_id"]
    
    # Retrieve markdown
    response = client.get(f"/api/companies/compare/{report_id}/markdown")
    assert response.status_code == 200
    data = response.json()
    assert "format" in data
    assert data["format"] == "markdown"
    assert "content" in data
    assert "Multi-Company Comparative Intelligence Report" in data["content"]


def test_get_latest_comparison_summary():
    """Test GET /api/companies/compare/latest/summary endpoint."""
    # Generate comparison
    client.post(
        "/api/companies/compare",
        json=[
            {"company_id": "a", "name": "A"},
            {"company_id": "b", "name": "B"},
        ]
    )
    
    # Retrieve summary
    response = client.get("/api/companies/compare/latest/summary")
    assert response.status_code == 200
    data = response.json()
    assert "companies" in data
    assert "strongest_company" in data
    assert "cluster_count" in data
    assert "key_insight" in data


def test_compare_with_empty_list():
    """Test error handling for empty company list."""
    response = client.post(
        "/api/companies/compare",
        json=[]
    )
    assert response.status_code == 400


def test_compare_with_too_many_companies():
    """Test error handling for too many companies."""
    companies = [
        {"company_id": f"c{i}", "name": f"Company {i}"}
        for i in range(15)
    ]
    response = client.post(
        "/api/companies/compare",
        json=companies
    )
    assert response.status_code == 400
