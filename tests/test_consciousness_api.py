"""
Tests for Corporate Consciousness API Endpoints (Step AE)

Tests all 12 REST API endpoints for consciousness operations
"""

import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


class TestConsciousnessEndpointExistence:
    """Test that all consciousness endpoints exist"""

    def test_generate_consciousness_endpoint_exists(self, client):
        """Test POST /consciousness/generate endpoint exists"""
        response = client.post(
            "/api/consciousness/generate",
            json={"period": "2026-01", "company_name": "TestCorp"},
        )
        # Should not 404
        assert response.status_code != 404

    def test_summary_endpoint_exists(self, client):
        """Test GET /consciousness/summary endpoint exists"""
        response = client.get("/api/consciousness/summary")
        assert response.status_code != 404

    def test_identity_endpoint_exists(self, client):
        """Test GET /consciousness/identity endpoint exists"""
        response = client.get("/api/consciousness/identity")
        assert response.status_code != 404

    def test_purpose_endpoint_exists(self, client):
        """Test GET /consciousness/purpose endpoint exists"""
        response = client.get("/api/consciousness/purpose")
        assert response.status_code != 404

    def test_direction_endpoint_exists(self, client):
        """Test GET /consciousness/direction endpoint exists"""
        response = client.get("/api/consciousness/direction")
        assert response.status_code != 404

    def test_assessment_endpoint_exists(self, client):
        """Test GET /consciousness/assessment endpoint exists"""
        response = client.get("/api/consciousness/assessment")
        assert response.status_code != 404

    def test_evolution_endpoint_exists(self, client):
        """Test GET /consciousness/evolution endpoint exists"""
        response = client.get("/api/consciousness/evolution")
        assert response.status_code != 404

    def test_statement_endpoint_exists(self, client):
        """Test GET /consciousness/statement endpoint exists"""
        response = client.get("/api/consciousness/statement")
        assert response.status_code != 404

    def test_metrics_endpoint_exists(self, client):
        """Test GET /consciousness/metrics endpoint exists"""
        response = client.get("/api/consciousness/metrics")
        assert response.status_code != 404

    def test_history_endpoint_exists(self, client):
        """Test GET /consciousness/history endpoint exists"""
        response = client.get("/api/consciousness/history")
        assert response.status_code != 404

    def test_markdown_endpoint_exists(self, client):
        """Test GET /consciousness/markdown endpoint exists"""
        response = client.get("/api/consciousness/markdown")
        assert response.status_code != 404

    def test_update_endpoint_exists(self, client):
        """Test POST /consciousness/update endpoint exists"""
        response = client.post(
            "/api/consciousness/update",
            json={"period": "2026-01", "company_name": "TestCorp"},
        )
        assert response.status_code != 404


class TestGenerateConsciousnessEndpoint:
    """Test consciousness generation endpoint"""

    def test_generate_consciousness_returns_200(self, client):
        """Test successful generation returns 200"""
        response = client.post(
            "/api/consciousness/generate",
            json={"period": "2026-01", "company_name": "TestCorp"},
        )
        assert response.status_code == 200

    def test_generate_consciousness_returns_valid_data(self, client):
        """Test generation returns valid consciousness data"""
        response = client.post(
            "/api/consciousness/generate",
            json={"period": "2026-01", "company_name": "TestCorp"},
        )
        data = response.json()
        
        assert "consciousness_id" in data
        assert "period" in data
        assert "company_name" in data
        assert "overall_score" in data
        assert "clarity_score" in data
        assert "coherence_score" in data

    def test_generate_consciousness_requires_period(self, client):
        """Test generation requires period"""
        response = client.post(
            "/api/consciousness/generate",
            json={"company_name": "TestCorp"},
        )
        assert response.status_code >= 400

    def test_generate_consciousness_requires_company_name(self, client):
        """Test generation requires company name"""
        response = client.post(
            "/api/consciousness/generate",
            json={"period": "2026-01"},
        )
        assert response.status_code >= 400


class TestSummaryEndpoint:
    """Test consciousness summary endpoint"""

    def test_summary_returns_200_when_exists(self, client):
        """Test summary returns 200 when consciousness exists"""
        # Generate first
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-02", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/summary")
        assert response.status_code == 200

    def test_summary_includes_key_fields(self, client):
        """Test summary includes key fields"""
        # Generate first
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-02", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/summary")
        data = response.json()
        
        assert "identity_statement" in data
        assert "purpose_statement" in data
        assert "strategic_direction" in data
        assert "overall_score" in data


class TestIdentityEndpoint:
    """Test identity statement endpoint"""

    def test_identity_returns_200_when_exists(self, client):
        """Test identity returns 200 when consciousness exists"""
        # Generate first
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-03", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/identity")
        assert response.status_code == 200

    def test_identity_includes_required_fields(self, client):
        """Test identity includes required fields"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-03", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/identity")
        data = response.json()
        
        assert "core_identity" in data
        assert "archetype" in data
        assert "brand_promise" in data
        assert "value_hierarchy" in data


class TestPurposeEndpoint:
    """Test purpose statement endpoint"""

    def test_purpose_returns_200_when_exists(self, client):
        """Test purpose returns 200 when consciousness exists"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-04", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/purpose")
        assert response.status_code == 200

    def test_purpose_includes_stakeholder_purposes(self, client):
        """Test purpose includes stakeholder focus"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-04", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/purpose")
        data = response.json()
        
        assert "mission" in data
        assert "vision" in data
        assert "stakeholder_purposes" in data


class TestDirectionEndpoint:
    """Test strategic direction endpoint"""

    def test_direction_returns_200_when_exists(self, client):
        """Test direction returns 200 when consciousness exists"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-05", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/direction")
        assert response.status_code == 200

    def test_direction_includes_strategy(self, client):
        """Test direction includes strategic information"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-05", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/direction")
        data = response.json()
        
        assert "primary_strategy" in data
        assert "strategic_focus_areas" in data
        assert "key_priorities" in data


class TestAssessmentEndpoint:
    """Test self-assessment endpoint"""

    def test_assessment_returns_200_when_exists(self, client):
        """Test assessment returns 200 when consciousness exists"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-06", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/assessment")
        assert response.status_code == 200

    def test_assessment_includes_swot(self, client):
        """Test assessment includes SWOT analysis"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-06", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/assessment")
        data = response.json()
        
        assert "overall_health" in data
        assert "strengths" in data or "swot" in data


class TestStatementEndpoint:
    """Test consciousness statement endpoint"""

    def test_statement_returns_200_when_exists(self, client):
        """Test statement returns 200 when consciousness exists"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-07", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/statement")
        assert response.status_code == 200

    def test_statement_includes_narratives(self, client):
        """Test statement includes narrative paragraphs"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-07", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/statement")
        data = response.json()
        
        # Should have narrative fields
        assert any(key in data for key in ["identity_narrative", "purpose_narrative", "direction_narrative"])


class TestMetricsEndpoint:
    """Test quality metrics endpoint"""

    def test_metrics_returns_200_when_exists(self, client):
        """Test metrics returns 200 when consciousness exists"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-08", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/metrics")
        assert response.status_code == 200

    def test_metrics_includes_quality_scores(self, client):
        """Test metrics includes all quality scores"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-08", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/metrics")
        data = response.json()
        
        # Should have various metrics
        assert len(data) > 0


class TestHistoryEndpoint:
    """Test consciousness history endpoint"""

    def test_history_returns_200(self, client):
        """Test history returns 200"""
        response = client.get("/api/consciousness/history")
        assert response.status_code == 200

    def test_history_respects_limit_param(self, client):
        """Test history respects limit parameter"""
        # Generate multiple records
        for i in range(1, 6):
            client.post(
                "/api/consciousness/generate",
                json={"period": f"2026-{i:02d}", "company_name": "TestCorp"},
            )
        
        response = client.get("/api/consciousness/history?limit=2")
        data = response.json()
        
        if isinstance(data, dict) and "history" in data:
            assert len(data["history"]) <= 2
        elif isinstance(data, list):
            assert len(data) <= 2


class TestMarkdownEndpoint:
    """Test markdown export endpoint"""

    def test_markdown_returns_200_when_exists(self, client):
        """Test markdown export returns 200 when consciousness exists"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-09", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/markdown")
        assert response.status_code == 200

    def test_markdown_response_is_text(self, client):
        """Test markdown export response is markdown format"""
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-09", "company_name": "TestCorp"},
        )
        
        response = client.get("/api/consciousness/markdown")
        
        # Should have markdown content
        assert isinstance(response.text, str)
        assert len(response.text) > 0


class TestUpdateEndpoint:
    """Test consciousness update endpoint"""

    def test_update_returns_200(self, client):
        """Test update returns 200"""
        response = client.post(
            "/api/consciousness/update",
            json={"period": "2026-10", "company_name": "TestCorp"},
        )
        assert response.status_code == 200

    def test_update_returns_updated_status(self, client):
        """Test update returns status message"""
        response = client.post(
            "/api/consciousness/update",
            json={"period": "2026-10", "company_name": "TestCorp"},
        )
        data = response.json()
        
        assert "status" in data or "period" in data or "consciousness_id" in data


class TestConsciousnessAPIErrorHandling:
    """Test API error handling"""

    def test_invalid_period_format_handled(self, client):
        """Test invalid period format is handled"""
        response = client.post(
            "/api/consciousness/generate",
            json={"period": "invalid", "company_name": "TestCorp"},
        )
        # Should return an error
        assert response.status_code >= 400

    def test_empty_company_name_handled(self, client):
        """Test empty company name is handled"""
        response = client.post(
            "/api/consciousness/generate",
            json={"period": "2026-01", "company_name": ""},
        )
        # Should return an error or use default
        assert response.status_code >= 400 or response.status_code == 200


class TestConsciousnessAPIIntegration:
    """Test API integration flows"""

    def test_full_workflow_generate_and_retrieve(self, client):
        """Test full workflow: generate and retrieve"""
        # Generate
        gen_response = client.post(
            "/api/consciousness/generate",
            json={"period": "2026-11", "company_name": "TestCorp"},
        )
        assert gen_response.status_code == 200
        
        # Retrieve summary
        sum_response = client.get("/api/consciousness/summary")
        assert sum_response.status_code == 200

    def test_multiple_endpoint_consistency(self, client):
        """Test multiple endpoints return consistent data"""
        # Generate
        client.post(
            "/api/consciousness/generate",
            json={"period": "2026-12", "company_name": "TestCorp"},
        )
        
        # Get different views
        summary_response = client.get("/api/consciousness/summary")
        metrics_response = client.get("/api/consciousness/metrics")
        
        assert summary_response.status_code == 200
        assert metrics_response.status_code == 200
        
        # Both should have score data
        summary_data = summary_response.json()
        metrics_data = metrics_response.json()
        
        assert "overall_score" in summary_data or "score" in str(summary_data).lower()
        assert len(metrics_data) > 0
