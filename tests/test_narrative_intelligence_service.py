"""
Tests for Narrative Intelligence Service
======================================

Tests for the narrative intelligence service that manages narrative
generation, persistence, retrieval, and export functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.backend.app.services.narrative_intelligence_service import NarrativeIntelligenceService
from src.backend.app.models.narrative_intelligence_model import (
    GeneratedNarrative,
    NarrativeAudience,
    NarrativeIntelligenceMetrics,
    NarrativeIntelligenceReport,
)
from src.backend.app.models.corporate_consciousness_evolution_model import ConsciousnessPhase
from src.backend.app.models.corporate_intent_model import CorporateIntent
from src.backend.app.models.executive_agent_model import ExecutiveDecisionResult
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.external_environment_model_v2 import ExternalEnvironmentState, PESTFactors


class TestNarrativeIntelligenceService:
    """Test narrative intelligence service functionality."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create service instance with temporary directory."""
        with patch.object(NarrativeIntelligenceService, 'NARRATIVES_DIR', tmp_path / 'narratives'):
            service = NarrativeIntelligenceService()
            yield service

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for testing."""
        return {
            'evolution_service': Mock(),
            'intent_service': Mock(),
            'agent_service': Mock(),
            'frontier_service': Mock(),
            'culture_service': Mock(),
            'environment_service': Mock(),
        }

    def test_service_initialization(self, service):
        """Test that service initializes properly."""
        assert service.engine is not None
        assert service.NARRATIVES_DIR.exists()
        assert service.NARRATIVES_FILE.exists()

    def test_generate_narrative_success(self, service, mock_dependencies):
        """Test successful narrative generation."""
        # Setup mocks
        mock_dependencies['evolution_service'].get_state.return_value = Mock(
            current_phase=ConsciousnessPhase.GROWING
        )
        mock_dependencies['intent_service'].get_current_intent.return_value = CorporateIntent(
            mission="Test mission"
        )
        mock_dependencies['agent_service'].get_latest_decision.return_value = ExecutiveDecisionResult(
            selected_candidate_id="strategy_001",
            selected_candidate_desc="Test decision",
            votes=[],
            aggregated_score=0.8,
            method="weighted_average",
            vote_distribution={"strategy_001": 0.8},
            supporting_roles=["CEO"],
            opposing_roles=[],
            all_scores={},
            timestamp=datetime.now()
        )
        mock_dependencies['frontier_service'].get_health_score.return_value = 0.8
        mock_dependencies['culture_service'].get_current_profile.return_value = CultureProfile(
            period="2024-01",
            aggressiveness_culture=0.5,
            risk_aversion_culture=0.5,
            brand_culture=0.5,
            cost_culture=0.5,
            people_culture=0.5,
            execution_culture=0.5,
            innovation_culture=0.5,
            stability_culture=0.5,
            notes="Test culture"
        )
        mock_dependencies['environment_service'].get_current_state.return_value = ExternalEnvironmentState(
            period="2024-01",
            pest=PESTFactors(political=0.2, economic=0.2, social=0.2, technological=0.2),
            competitors=[],
            shocks=[],
            market_growth_modifier=1.0,
            risk_modifier=0.8
        )

        # Mock service dependencies by setting private attributes
        service._evolution_service = mock_dependencies['evolution_service']
        service._intent_service = mock_dependencies['intent_service']
        service._agent_service = mock_dependencies['agent_service']
        service._frontier_service = mock_dependencies['frontier_service']
        service._culture_service = mock_dependencies['culture_service']
        service._environment_service = mock_dependencies['environment_service']

        narrative = service.generate_narrative(NarrativeAudience.INVESTORS)

        assert isinstance(narrative, GeneratedNarrative)
        assert narrative.audience == NarrativeAudience.INVESTORS
        assert len(narrative.text) > 0

    def test_generate_narrative_fallback_on_failure(self, service):
        """Test that service provides fallback narrative when dependencies fail."""
        # Mock all services to raise exceptions
        service._evolution_service = Mock(side_effect=Exception("Service unavailable"))
        
        narrative = service.generate_narrative(NarrativeAudience.CRISIS)

        assert isinstance(narrative, GeneratedNarrative)
        assert narrative.audience == NarrativeAudience.CRISIS
        # The service should gracefully handle the failure
        assert len(narrative.text) > 0

    def test_get_narrative_by_id(self, service):
        """Test retrieving narrative by ID."""
        # Create and save a test narrative
        test_narrative = GeneratedNarrative(
            audience=NarrativeAudience.EMPLOYEES,
            style=NarrativeIntelligenceService().engine._select_style(NarrativeAudience.EMPLOYEES),
            text="Test narrative content",
            key_messages=["Test message"],
            tone_markers=["inspirational"]
        )

        service._save_narrative(test_narrative)

        # Retrieve the narrative
        retrieved = service.get_narrative(test_narrative.narrative_id)

        assert retrieved is not None
        assert retrieved.narrative_id == test_narrative.narrative_id
        assert retrieved.audience == test_narrative.audience

    def test_get_narrative_history(self, service):
        """Test retrieving narrative history."""
        # Create multiple test narratives
        narratives = []
        for i in range(3):
            narrative = GeneratedNarrative(
                audience=NarrativeAudience.INVESTORS,
                style=NarrativeIntelligenceService().engine._select_style(NarrativeAudience.INVESTORS),
                text=f"Test narrative {i}",
                key_messages=[f"Message {i}"],
                tone_markers=["analytical"]
            )
            service._save_narrative(narrative)
            narratives.append(narrative)

        # Retrieve history
        history = service.get_narrative_history(limit=2)

        assert len(history) == 2
        # Should be sorted by timestamp (most recent first)
        assert history[0].timestamp >= history[1].timestamp

    def test_get_narratives_by_audience(self, service):
        """Test retrieving narratives by audience."""
        # Create narratives for different audiences
        audiences = [NarrativeAudience.INVESTORS, NarrativeAudience.EMPLOYEES, NarrativeAudience.INVESTORS]

        for audience in audiences:
            narrative = GeneratedNarrative(
                audience=audience,
                style=NarrativeIntelligenceService().engine._select_style(audience),
                text=f"Test for {audience.value}",
                key_messages=["Test"],
                tone_markers=["test"]
            )
            service._save_narrative(narrative)

        # Retrieve investor narratives
        investor_narratives = service.get_narratives_by_audience(NarrativeAudience.INVESTORS, limit=5)

        assert len(investor_narratives) == 2
        assert all(n.audience == NarrativeAudience.INVESTORS for n in investor_narratives)

    def test_export_narrative_markdown(self, service):
        """Test exporting narrative as markdown."""
        # Create and save a test narrative
        test_narrative = GeneratedNarrative(
            audience=NarrativeAudience.CUSTOMERS,
            style=NarrativeIntelligenceService().engine._select_style(NarrativeAudience.CUSTOMERS),
            text="We are committed to serving our customers with excellence.",
            key_messages=["Customer commitment", "Service excellence"],
            tone_markers=["confident", "committed"]
        )

        service._save_narrative(test_narrative)

        # Export as markdown
        markdown = service.export_narrative_markdown(test_narrative.narrative_id)

        assert markdown is not None
        assert "# Narrative for CUSTOMERS" in markdown
        assert "Customer commitment" in markdown
        assert "confident" in markdown

    def test_get_narrative_metrics(self, service):
        """Test getting narrative metrics."""
        # Create test narratives
        audiences = [NarrativeAudience.INVESTORS, NarrativeAudience.EMPLOYEES, NarrativeAudience.INVESTORS]

        for audience in audiences:
            narrative = GeneratedNarrative(
                audience=audience,
                style=NarrativeIntelligenceService().engine._select_style(audience),
                text="Test content",
                key_messages=["Test"],
                tone_markers=["test"]
            )
            service._save_narrative(narrative)

        metrics = service.get_narrative_metrics()

        assert isinstance(metrics, NarrativeIntelligenceMetrics)
        assert metrics.total_narratives == 3
        assert metrics.audience_distribution[NarrativeAudience.INVESTORS.value] == 2
        assert metrics.audience_distribution[NarrativeAudience.EMPLOYEES.value] == 1

    def test_generate_narrative_report(self, service):
        """Test generating comprehensive narrative report."""
        # Create test narratives
        for audience in NarrativeAudience:
            narrative = GeneratedNarrative(
                audience=audience,
                style=NarrativeIntelligenceService().engine._select_style(audience),
                text=f"Test for {audience.value}",
                key_messages=["Test message"],
                tone_markers=["test"]
            )
            service._save_narrative(narrative)

        report = service.generate_narrative_report()

        assert isinstance(report, NarrativeIntelligenceReport)
        assert report.metrics.total_narratives == len(NarrativeAudience)
        assert len(report.recent_narratives) > 0
        assert isinstance(report.audience_effectiveness, dict)
        assert isinstance(report.recommendations, list)

    def test_persistence_round_trip(self, service):
        """Test that narratives can be saved and loaded correctly."""
        original = GeneratedNarrative(
            audience=NarrativeAudience.PUBLIC,
            style=NarrativeIntelligenceService().engine._select_style(NarrativeAudience.PUBLIC),
            text="Original narrative content with special characters: éñ中文",
            key_messages=["Message 1", "Message 2"],
            tone_markers=["formal", "confident"]
        )

        # Save and reload
        service._save_narrative(original)
        loaded = service.get_narrative(original.narrative_id)

        assert loaded is not None
        assert loaded.narrative_id == original.narrative_id
        assert loaded.audience == original.audience
        assert loaded.style == original.style
        assert loaded.text == original.text
        assert loaded.key_messages == original.key_messages
        assert loaded.tone_markers == original.tone_markers

    def test_history_limit_enforcement(self, service):
        """Test that history retrieval respects limits."""
        # Create many narratives
        for i in range(10):
            narrative = GeneratedNarrative(
                audience=NarrativeAudience.INVESTORS,
                style=NarrativeIntelligenceService().engine._select_style(NarrativeAudience.INVESTORS),
                text=f"Narrative {i}",
                key_messages=["Test"],
                tone_markers=["test"]
            )
            service._save_narrative(narrative)

        # Test limit enforcement
        history = service.get_narrative_history(limit=3)
        assert len(history) == 3

        history = service.get_narrative_history(limit=100)
        assert len(history) == 10  # Should not exceed available

    def test_audience_filtering(self, service):
        """Test that audience filtering works correctly."""
        # Create mixed audience narratives
        audiences_to_create = [
            NarrativeAudience.INVESTORS,
            NarrativeAudience.EMPLOYEES,
            NarrativeAudience.INVESTORS,
            NarrativeAudience.CUSTOMERS,
            NarrativeAudience.INVESTORS
        ]

        for audience in audiences_to_create:
            narrative = GeneratedNarrative(
                audience=audience,
                style=NarrativeIntelligenceService().engine._select_style(audience),
                text=f"Test for {audience.value}",
                key_messages=["Test"],
                tone_markers=["test"]
            )
            service._save_narrative(narrative)

        # Test filtering
        investor_narratives = service.get_narratives_by_audience(NarrativeAudience.INVESTORS)
        employee_narratives = service.get_narratives_by_audience(NarrativeAudience.EMPLOYEES)
        customer_narratives = service.get_narratives_by_audience(NarrativeAudience.CUSTOMERS)

        assert len(investor_narratives) == 3
        assert len(employee_narratives) == 1
        assert len(customer_narratives) == 1

        assert all(n.audience == NarrativeAudience.INVESTORS for n in investor_narratives)
        assert all(n.audience == NarrativeAudience.EMPLOYEES for n in employee_narratives)
        assert all(n.audience == NarrativeAudience.CUSTOMERS for n in customer_narratives)


class TestServiceErrorHandling:
    """Test error handling in narrative intelligence service."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create service instance with temporary directory."""
        with patch.object(NarrativeIntelligenceService, 'NARRATIVES_DIR', tmp_path / 'narratives'):
            service = NarrativeIntelligenceService()
            yield service

    def test_get_nonexistent_narrative(self, service):
        """Test retrieving non-existent narrative returns None."""
        result = service.get_narrative("nonexistent-id")
        assert result is None

    def test_export_nonexistent_narrative_markdown(self, service):
        """Test exporting non-existent narrative returns None."""
        result = service.export_narrative_markdown("nonexistent-id")
        assert result is None

    def test_corrupted_persistence_file_handling(self, service):
        """Test handling of corrupted persistence file."""
        # Write invalid JSON to persistence file
        with open(service.NARRATIVES_FILE, 'w') as f:
            f.write("invalid json content")

        # Should handle gracefully and return empty list
        narratives = service._load_narratives()
        assert narratives == []

    def test_empty_narratives_file_handling(self, service):
        """Test handling of empty narratives file."""
        # Ensure file exists but is empty
        service.NARRATIVES_FILE.write_text("")

        narratives = service._load_narratives()
        assert narratives == []

    def test_metrics_with_no_narratives(self, service):
        """Test metrics calculation when no narratives exist."""
        metrics = service.get_narrative_metrics()

        assert metrics.total_narratives == 0
        assert metrics.audience_distribution == {}
        assert metrics.style_distribution == {}
        assert metrics.last_generated is None