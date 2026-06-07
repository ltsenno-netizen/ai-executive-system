"""
Tests for Narrative Intelligence API
===================================

Tests for the REST API endpoints of the narrative intelligence system.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.backend.app.main import app
from src.backend.app.models.narrative_intelligence_model import (
    GeneratedNarrative,
    NarrativeAudience,
    NarrativeStyle,
)
from src.backend.app.services.narrative_intelligence_service import NarrativeIntelligenceService


class TestNarrativeIntelligenceAPI:
    """Test narrative intelligence API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_service(self):
        """Create mock service for testing."""
        return Mock(spec=NarrativeIntelligenceService)

    def test_generate_narrative_endpoint_exists(self, client):
        """Test that generate narrative endpoint exists."""
        response = client.post("/api/narrative/generate/INVESTORS")
        # Should not return 404 (may return other errors if service unavailable)
        assert response.status_code != 404

    def test_get_narrative_endpoint_exists(self, client):
        """Test that get narrative endpoint exists."""
        response = client.get("/api/narrative/test-id")
        assert response.status_code != 404

    def test_get_narrative_history_endpoint_exists(self, client):
        """Test that narrative history endpoint exists."""
        response = client.get("/api/narrative/history")
        assert response.status_code != 404

    def test_export_markdown_endpoint_exists(self, client):
        """Test that markdown export endpoint exists."""
        response = client.get("/api/narrative/test-id/markdown")
        assert response.status_code != 404

    def test_get_audiences_endpoint_exists(self, client):
        """Test that audiences endpoint exists."""
        response = client.get("/api/narrative/audiences")
        assert response.status_code == 200

    def test_get_styles_endpoint_exists(self, client):
        """Test that styles endpoint exists."""
        response = client.get("/api/narrative/styles")
        assert response.status_code == 200

    def test_get_metrics_endpoint_exists(self, client):
        """Test that metrics endpoint exists."""
        response = client.get("/api/narrative/metrics")
        assert response.status_code != 404

    def test_get_report_endpoint_exists(self, client):
        """Test that report endpoint exists."""
        response = client.get("/api/narrative/report")
        assert response.status_code != 404

    def test_get_audiences_returns_valid_data(self, client):
        """Test that audiences endpoint returns valid data."""
        response = client.get("/api/narrative/audiences")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check structure of first item
        first_audience = data[0]
        assert "audience" in first_audience
        assert "description" in first_audience

    def test_get_styles_returns_valid_data(self, client):
        """Test that styles endpoint returns valid data."""
        response = client.get("/api/narrative/styles")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check structure of first item
        first_style = data[0]
        assert "style" in first_style
        assert "description" in first_style

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_generate_narrative_success(self, mock_service, client):
        """Test successful narrative generation."""
        # Mock the service response
        mock_narrative = GeneratedNarrative(
            audience=NarrativeAudience.INVESTORS,
            style=NarrativeStyle.ANALYTICAL,
            text="Test narrative content for investors.",
            key_messages=["Strong financial performance", "Strategic investments"],
            tone_markers=["confident", "analytical"]
        )
        mock_service.generate_narrative.return_value = mock_narrative

        response = client.post("/api/narrative/generate/INVESTORS")

        assert response.status_code == 200
        data = response.json()
        assert data["audience"] == "INVESTORS"
        assert data["style"] == "ANALYTICAL"
        assert "narrative_id" in data
        assert len(data["text"]) > 0

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_generate_narrative_all_audiences(self, mock_service, client):
        """Test narrative generation for all audiences."""
        mock_narrative = GeneratedNarrative(
            audience=NarrativeAudience.EMPLOYEES,
            style=NarrativeStyle.INSPIRATIONAL,
            text="Test employee narrative.",
            key_messages=["Team collaboration"],
            tone_markers=["inspirational"]
        )
        mock_service.generate_narrative.return_value = mock_narrative

        for audience in NarrativeAudience:
            response = client.post(f"/api/narrative/generate/{audience.value}")
            assert response.status_code == 200

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_get_narrative_success(self, mock_service, client):
        """Test successful narrative retrieval."""
        mock_narrative = GeneratedNarrative(
            narrative_id="test-id-123",
            audience=NarrativeAudience.CUSTOMERS,
            style=NarrativeStyle.CONFIDENT,
            text="Test customer narrative.",
            key_messages=["Customer satisfaction"],
            tone_markers=["confident"]
        )
        mock_service.get_narrative.return_value = mock_narrative

        response = client.get("/api/narrative/test-id-123")

        assert response.status_code == 200
        data = response.json()
        assert data["narrative_id"] == "test-id-123"
        assert data["audience"] == "CUSTOMERS"

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_get_narrative_not_found(self, mock_service, client):
        """Test narrative retrieval when not found."""
        mock_service.get_narrative.return_value = None

        response = client.get("/api/narrative/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_get_narrative_history(self, mock_service, client):
        """Test narrative history retrieval."""
        mock_narratives = [
            GeneratedNarrative(
                audience=NarrativeAudience.INVESTORS,
                style=NarrativeStyle.ANALYTICAL,
                text=f"Narrative {i}",
                key_messages=["Test"],
                tone_markers=["test"]
            )
            for i in range(3)
        ]
        mock_service.get_narrative_history.return_value = mock_narratives

        response = client.get("/api/narrative/history")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_get_narrative_history_with_limit(self, mock_service, client):
        """Test narrative history with limit parameter."""
        mock_narratives = [
            GeneratedNarrative(
                audience=NarrativeAudience.EMPLOYEES,
                style=NarrativeStyle.INSPIRATIONAL,
                text=f"Limited narrative {i}",
                key_messages=["Test"],
                tone_markers=["test"]
            )
            for i in range(2)
        ]
        mock_service.get_narrative_history.return_value = mock_narratives

        response = client.get("/api/narrative/history?limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_export_markdown_success(self, mock_service, client):
        """Test successful markdown export."""
        mock_markdown = """# Narrative for INVESTORS

**Generated:** 2024-01-15 10:30:00 UTC
**Style:** ANALYTICAL

## Narrative Text

Test narrative content.

## Key Messages
- Strong performance
- Strategic focus

## Tone Markers
confident, analytical
"""
        mock_service.export_narrative_markdown.return_value = mock_markdown

        response = client.get("/api/narrative/test-id/markdown")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert "# Narrative for INVESTORS" in response.text

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_export_markdown_not_found(self, mock_service, client):
        """Test markdown export when narrative not found."""
        mock_service.export_narrative_markdown.return_value = None

        response = client.get("/api/narrative/nonexistent-id/markdown")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_get_narrative_metrics(self, mock_service, client):
        """Test metrics retrieval."""
        from src.backend.app.models.narrative_intelligence_model import NarrativeIntelligenceMetrics

        mock_metrics = NarrativeIntelligenceMetrics(
            total_narratives=5,
            audience_distribution={"INVESTORS": 2, "EMPLOYEES": 3},
            style_distribution={"ANALYTICAL": 2, "INSPIRATIONAL": 3},
            avg_generation_time=2.5,
            last_generated=None
        )
        mock_service.get_narrative_metrics.return_value = mock_metrics

        response = client.get("/api/narrative/metrics")

        assert response.status_code == 200
        data = response.json()
        assert data["total_narratives"] == 5
        assert data["audience_distribution"]["INVESTORS"] == 2

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_generate_narrative_report(self, mock_service, client):
        """Test report generation."""
        from src.backend.app.models.narrative_intelligence_model import NarrativeIntelligenceReport

        mock_report = NarrativeIntelligenceReport(
            period="last_30_days",
            metrics=NarrativeIntelligenceService().get_narrative_metrics(),
            recent_narratives=[],
            audience_effectiveness={},
            recommendations=["Increase narrative generation frequency"]
        )
        mock_service.generate_narrative_report.return_value = mock_report

        response = client.get("/api/narrative/report")

        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "last_30_days"
        assert "recommendations" in data

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_get_narratives_by_audience(self, mock_service, client):
        """Test audience-specific narrative retrieval."""
        mock_narratives = [
            GeneratedNarrative(
                audience=NarrativeAudience.INVESTORS,
                style=NarrativeStyle.ANALYTICAL,
                text="Investor narrative content",
                key_messages=["Financial performance"],
                tone_markers=["analytical"]
            )
        ]
        mock_service.get_narratives_by_audience.return_value = mock_narratives

        response = client.get("/api/narrative/audience/INVESTORS")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["audience"] == "INVESTORS"

    def test_parameter_validation_limit(self, client):
        """Test parameter validation for limit."""
        # Valid limit
        response = client.get("/api/narrative/history?limit=50")
        assert response.status_code in [200, 404]  # 404 is OK if no narratives

        # Invalid limit (too high)
        response = client.get("/api/narrative/history?limit=500")
        assert response.status_code == 422  # Validation error

        # Invalid limit (too low)
        response = client.get("/api/narrative/history?limit=0")
        assert response.status_code == 422  # Validation error

    def test_invalid_audience_generation(self, client):
        """Test generation with invalid audience."""
        response = client.post("/api/narrative/generate/INVALID_AUDIENCE")
        assert response.status_code == 422  # Validation error

    def test_audience_enum_values(self, client):
        """Test that all valid audience values work."""
        audiences_response = client.get("/api/narrative/audiences")
        audiences_data = audiences_response.json()

        audience_values = [item["audience"] for item in audiences_data]

        for audience_value in audience_values:
            response = client.post(f"/api/narrative/generate/{audience_value}")
            # Should not be a 422 validation error for invalid audience
            assert response.status_code != 422


class TestAPIErrorHandling:
    """Test error handling in narrative intelligence API."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_generate_narrative_service_error(self, mock_service, client):
        """Test handling of service errors during generation."""
        mock_service.generate_narrative.side_effect = Exception("Service unavailable")

        response = client.post("/api/narrative/generate/INVESTORS")

        assert response.status_code == 500
        assert "failed to generate narrative" in response.json()["detail"].lower()

    @patch('src.backend.app.routes.narrative_intelligence.service')
    def test_get_narrative_service_error(self, mock_service, client):
        """Test handling of service errors during retrieval."""
        mock_service.get_narrative.side_effect = Exception("Database error")

        response = client.get("/api/narrative/test-id")

        assert response.status_code == 500

    def test_malformed_narrative_id(self, client):
        """Test handling of malformed narrative IDs."""
        response = client.get("/api/narrative/invalid-id-with-special-chars!@#")
        # Should handle gracefully (may return 404 or 500 depending on implementation)
        assert response.status_code in [404, 500]

    def test_empty_history_response(self, client):
        """Test response when no narrative history exists."""
        # This would depend on actual service state
        # If service returns empty list, should get 200 with empty array
        response = client.get("/api/narrative/history")
        assert response.status_code in [200, 404]  # 404 if service fails, 200 if empty