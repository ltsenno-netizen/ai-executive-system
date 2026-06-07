"""
Tests for Narrative Intelligence Dashboard Integration
====================================================

Tests for the integration of narrative intelligence into the executive dashboard.
"""

import pytest
from unittest.mock import Mock, patch

from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService
from src.backend.app.models.executive_dashboard_model import NarrativeIntelligenceSummary
from src.backend.app.models.narrative_intelligence_model import (
    GeneratedNarrative,
    NarrativeAudience,
    NarrativeStyle,
)
from src.backend.app.services.narrative_intelligence_service import NarrativeIntelligenceService


class TestDashboardNarrativeIntelligenceIntegration:
    """Test narrative intelligence integration with executive dashboard."""

    @pytest.fixture
    def dashboard_service(self):
        """Create dashboard service instance."""
        return ExecutiveDashboardService()

    @pytest.fixture
    def mock_narrative_service(self):
        """Create mock narrative intelligence service."""
        return Mock(spec=NarrativeIntelligenceService)

    def test_dashboard_includes_narrative_intelligence_field(self, dashboard_service):
        """Test that dashboard includes narrative intelligence field."""
        # This test may fail if narrative service is not available
        # but the field should exist in the model
        dashboard = dashboard_service.build_dashboard(month=1, include_forecast=False)

        # Check that the field exists (may be None if service unavailable)
        assert hasattr(dashboard, 'narrative_intelligence')

    @patch('src.backend.app.services.executive_dashboard_service.NarrativeIntelligenceService')
    def test_aggregate_narrative_intelligence_success(self, mock_service_class, dashboard_service):
        """Test successful aggregation of narrative intelligence data."""
        # Mock the service instance
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Mock service responses
        mock_service.get_narratives_by_audience.side_effect = lambda audience, limit: [
            GeneratedNarrative(
                audience=audience,
                style=NarrativeStyle.ANALYTICAL if audience == NarrativeAudience.INVESTORS else NarrativeStyle.INSPIRATIONAL,
                text=f"Sample narrative for {audience.value}",
                key_messages=["Key message 1", "Key message 2"],
                tone_markers=["confident", "analytical"]
            )
        ]

        mock_service.get_narrative_metrics.return_value = Mock(
            total_narratives=8,
            last_generated=None
        )

        mock_service.get_narrative_history.return_value = [
            GeneratedNarrative(
                audience=NarrativeAudience.INVESTORS,
                style=NarrativeStyle.ANALYTICAL,
                text="Recent narrative",
                key_messages=["Recent key message"],
                tone_markers=["analytical"]
            )
        ]

        # Test the aggregation method
        result = dashboard_service.aggregate_narrative_intelligence_summary()

        assert result is not None
        assert isinstance(result, NarrativeIntelligenceSummary)
        assert result.total_narratives == 8
        assert len(result.recent_audiences) > 0
        assert len(result.key_messages) > 0
        assert len(result.tone_markers) > 0

    @patch('src.backend.app.services.executive_dashboard_service.NarrativeIntelligenceService')
    def test_aggregate_narrative_intelligence_service_failure(self, mock_service_class, dashboard_service):
        """Test graceful handling when narrative intelligence service fails."""
        # Mock service to raise exception
        mock_service_class.side_effect = Exception("Service unavailable")

        result = dashboard_service.aggregate_narrative_intelligence_summary()

        # Should return None gracefully
        assert result is None

    @patch('src.backend.app.services.executive_dashboard_service.NarrativeIntelligenceService')
    def test_aggregate_narrative_intelligence_partial_data(self, mock_service_class, dashboard_service):
        """Test handling of partial data from narrative service."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Mock some methods to succeed, others to fail
        mock_service.get_narratives_by_audience.side_effect = Exception("Partial failure")
        mock_service.get_narrative_metrics.return_value = Mock(
            total_narratives=3,
            last_generated=None
        )
        mock_service.get_narrative_history.return_value = []

        result = dashboard_service.aggregate_narrative_intelligence_summary()

        # Should still return summary with available data
        assert result is not None
        assert result.total_narratives == 3
        assert result.latest_narratives == {}  # Empty due to failure

    def test_narrative_intelligence_summary_model(self):
        """Test the NarrativeIntelligenceSummary model structure."""
        summary = NarrativeIntelligenceSummary(
            latest_narratives={
                "INVESTORS": "We remain committed to delivering value...",
                "EMPLOYEES": "Together we will achieve excellence..."
            },
            recent_audiences=["INVESTORS", "EMPLOYEES", "CUSTOMERS"],
            total_narratives=15,
            last_generation=None,
            key_messages=["Commitment to stakeholders", "Innovation focus", "Team collaboration"],
            tone_markers=["confident", "inspirational", "analytical"],
            frontier_reflection=0.75,
            intent_alignment=0.8
        )

        assert summary.latest_narratives["INVESTORS"] is not None
        assert len(summary.recent_audiences) == 3
        assert summary.total_narratives == 15
        assert len(summary.key_messages) == 3
        assert len(summary.tone_markers) == 3
        assert summary.frontier_reflection == 0.75
        assert summary.intent_alignment == 0.8

    @patch('src.backend.app.services.executive_dashboard_service.NarrativeIntelligenceService')
    def test_dashboard_build_includes_narrative_intelligence(self, mock_service_class, dashboard_service):
        """Test that dashboard build includes narrative intelligence data."""
        # Mock successful narrative service
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_service.get_narratives_by_audience.return_value = []
        mock_service.get_narrative_metrics.return_value = Mock(
            total_narratives=0,
            last_generated=None
        )
        mock_service.get_narrative_history.return_value = []

        dashboard = dashboard_service.build_dashboard(month=1, include_forecast=False)

        # Check that narrative_intelligence field exists
        assert hasattr(dashboard, 'narrative_intelligence')
        # May be None if no data, but field should exist
        assert dashboard.narrative_intelligence is None or isinstance(dashboard.narrative_intelligence, NarrativeIntelligenceSummary)

    @patch('src.backend.app.services.executive_dashboard_service.NarrativeIntelligenceService')
    def test_narrative_intelligence_data_flow(self, mock_service_class, dashboard_service):
        """Test the complete data flow from service to dashboard."""
        # Setup comprehensive mock data
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Mock narratives for different audiences
        def mock_get_narratives(audience, limit=1):
            narratives = {
                NarrativeAudience.INVESTORS: GeneratedNarrative(
                    audience=NarrativeAudience.INVESTORS,
                    style=NarrativeStyle.ANALYTICAL,
                    text="Our financial performance demonstrates strong value creation for shareholders.",
                    key_messages=["Strong financial performance", "Value creation"],
                    tone_markers=["analytical", "confident"]
                ),
                NarrativeAudience.EMPLOYEES: GeneratedNarrative(
                    audience=NarrativeAudience.EMPLOYEES,
                    style=NarrativeStyle.INSPIRATIONAL,
                    text="Together, we are building an organization that inspires innovation and excellence.",
                    key_messages=["Team collaboration", "Innovation focus"],
                    tone_markers=["inspirational", "motivational"]
                ),
                NarrativeAudience.CUSTOMERS: GeneratedNarrative(
                    audience=NarrativeAudience.CUSTOMERS,
                    style=NarrativeStyle.CONFIDENT,
                    text="We are committed to delivering exceptional value and service to our customers.",
                    key_messages=["Customer commitment", "Service excellence"],
                    tone_markers=["confident", "professional"]
                )
            }
            return [narratives.get(audience, GeneratedNarrative(
                audience=audience,
                style=NarrativeStyle.FORMAL,
                text="Default narrative.",
                key_messages=["Default"],
                tone_markers=["formal"]
            ))]

        mock_service.get_narratives_by_audience.side_effect = mock_get_narratives

        mock_service.get_narrative_metrics.return_value = Mock(
            total_narratives=12,
            last_generated=None
        )

        mock_service.get_narrative_history.return_value = [
            GeneratedNarrative(
                audience=NarrativeAudience.INVESTORS,
                style=NarrativeStyle.ANALYTICAL,
                text="Recent investor communication.",
                key_messages=["Recent key message"],
                tone_markers=["analytical"]
            )
        ]

        # Test aggregation
        summary = dashboard_service.aggregate_narrative_intelligence_summary()

        assert summary is not None
        assert summary.total_narratives == 12
        assert "INVESTORS" in summary.latest_narratives
        assert "EMPLOYEES" in summary.latest_narratives
        assert "CUSTOMERS" in summary.latest_narratives
        assert len(summary.recent_audiences) > 0
        assert len(summary.key_messages) > 0
        assert len(summary.tone_markers) > 0

        # Verify content is properly truncated for dashboard
        for audience_text in summary.latest_narratives.values():
            assert len(audience_text) <= 203  # 200 + "..."

    def test_narrative_intelligence_dashboard_display_fields(self):
        """Test that dashboard display fields are properly structured."""
        summary = NarrativeIntelligenceSummary(
            latest_narratives={"INVESTORS": "Financial narrative..."},
            recent_audiences=["INVESTORS", "EMPLOYEES"],
            total_narratives=5,
            last_generation=None,
            key_messages=["Message 1", "Message 2", "Message 3"],
            tone_markers=["confident", "analytical"],
            frontier_reflection=0.6,
            intent_alignment=0.7
        )

        # Test field access (simulating dashboard display)
        assert summary.latest_narratives["INVESTORS"] == "Financial narrative..."
        assert len(summary.recent_audiences) == 2
        assert summary.total_narratives == 5
        assert len(summary.key_messages) == 3
        assert len(summary.tone_markers) == 2
        assert summary.frontier_reflection == 0.6
        assert summary.intent_alignment == 0.7


class TestDashboardIntegrationErrorHandling:
    """Test error handling in dashboard narrative intelligence integration."""

    @pytest.fixture
    def dashboard_service(self):
        return ExecutiveDashboardService()

    @patch('src.backend.app.services.executive_dashboard_service.NarrativeIntelligenceService')
    def test_dashboard_build_handles_narrative_service_failure(self, mock_service_class, dashboard_service):
        """Test that dashboard build handles narrative service failures gracefully."""
        mock_service_class.side_effect = ImportError("Narrative service not available")

        # Dashboard should still build successfully
        dashboard = dashboard_service.build_dashboard(month=1, include_forecast=False)

        assert dashboard is not None
        assert hasattr(dashboard, 'narrative_intelligence')
        # Field should be None when service unavailable
        assert dashboard.narrative_intelligence is None

    @patch('src.backend.app.services.executive_dashboard_service.NarrativeIntelligenceService')
    def test_partial_narrative_data_handling(self, mock_service_class, dashboard_service):
        """Test handling when only partial narrative data is available."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Some methods succeed, others fail
        mock_service.get_narratives_by_audience.side_effect = [
            [GeneratedNarrative(audience=NarrativeAudience.INVESTORS, style=NarrativeStyle.ANALYTICAL,
                              text="Investor narrative", key_messages=["Test"], tone_markers=["test"])],
            Exception("Service temporarily unavailable"),  # Employees fail
            []  # Customers empty
        ]
        mock_service.get_narrative_metrics.return_value = Mock(total_narratives=1, last_generated=None)
        mock_service.get_narrative_history.return_value = []

        summary = dashboard_service.aggregate_narrative_intelligence_summary()

        # Should still create summary with available data
        assert summary is not None
        assert summary.total_narratives == 1
        assert "INVESTORS" in summary.latest_narratives
        # Other audiences may not be included due to failures