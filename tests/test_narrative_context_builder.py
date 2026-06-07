"""
Tests for Narrative Intelligence Context Builder
===============================================

Tests for the narrative context building functionality that integrates
all system components (consciousness, evolution, intent, agents, frontier, culture, environment).
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.backend.app.services.narrative_intelligence_engine import NarrativeIntelligenceEngine
from src.backend.app.models.narrative_intelligence_model import (
    NarrativeAudience,
    NarrativeContext,
    NarrativeStyle,
)
from src.backend.app.models.corporate_consciousness_evolution_model import ConsciousnessPhase
from src.backend.app.models.corporate_intent_model import CorporateIntent
from src.backend.app.models.executive_agent_model import ExecutiveDecisionResult
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.external_environment_model_v2 import ExternalEnvironmentState, PESTFactors


class TestNarrativeContextBuilder:
    """Test narrative context building functionality."""

    @pytest.fixture
    def engine(self):
        """Create narrative intelligence engine instance."""
        return NarrativeIntelligenceEngine()

    @pytest.fixture
    def mock_system_components(self):
        """Create mock system components for testing."""
        return {
            'phase': ConsciousnessPhase.GROWING,
            'intent': CorporateIntent(
                mission="To create sustainable value",
                vision="Leading innovation",
                values=["Innovation", "Integrity", "Excellence"]
            ),
            'decision': ExecutiveDecisionResult(
                selected_candidate_id="strategy_001",
                selected_candidate_desc="Approved strategic investment in R&D",
                votes=[],
                aggregated_score=0.85,
                method="weighted_average",
                vote_distribution={"strategy_001": 0.85},
                supporting_roles=["CEO", "CTO"],
                opposing_roles=[],
                all_scores={},
                timestamp=datetime.now()
            ),
            'frontier_health': 0.75,
            'culture_profile': CultureProfile(
                period="2024-01",
                aggressiveness_culture=0.6,
                risk_aversion_culture=0.4,
                brand_culture=0.8,
                cost_culture=0.5,
                people_culture=0.7,
                execution_culture=0.65,
                innovation_culture=0.75,
                stability_culture=0.55,
                notes="Dynamic and evolving culture"
            ),
            'environment_state': ExternalEnvironmentState(
                period="2024-01",
                pest=PESTFactors(political=0.3, economic=0.4, social=0.5, technological=0.7),
                competitors=[],
                shocks=[],
                market_growth_modifier=1.0,
                risk_modifier=0.8
            )
        }

    def test_build_context_investors(self, engine, mock_system_components):
        """Test building context for investor audience."""
        context = engine.build_narrative_context(
            audience=NarrativeAudience.INVESTORS,
            **mock_system_components
        )

        assert context.audience == NarrativeAudience.INVESTORS
        assert context.style == NarrativeStyle.ANALYTICAL
        assert context.phase == ConsciousnessPhase.GROWING
        assert context.intent == mock_system_components['intent']
        assert context.decision == mock_system_components['decision']
        assert context.frontier_health == 0.75
        assert context.culture_profile == mock_system_components['culture_profile']
        assert context.environment_state == mock_system_components['environment_state']

    def test_build_context_employees(self, engine, mock_system_components):
        """Test building context for employee audience."""
        context = engine.build_narrative_context(
            audience=NarrativeAudience.EMPLOYEES,
            **mock_system_components
        )

        assert context.audience == NarrativeAudience.EMPLOYEES
        assert context.style == NarrativeStyle.INSPIRATIONAL

    def test_build_context_crisis(self, engine, mock_system_components):
        """Test building context for crisis audience."""
        context = engine.build_narrative_context(
            audience=NarrativeAudience.CRISIS,
            **mock_system_components
        )

        assert context.audience == NarrativeAudience.CRISIS
        assert context.style == NarrativeStyle.TRANSPARENT

    def test_build_context_transformation(self, engine, mock_system_components):
        """Test building context for transformation audience."""
        context = engine.build_narrative_context(
            audience=NarrativeAudience.TRANSFORMATION,
            **mock_system_components
        )

        assert context.audience == NarrativeAudience.TRANSFORMATION
        assert context.style == NarrativeStyle.CONFIDENT

    def test_build_context_growth(self, engine, mock_system_components):
        """Test building context for growth audience."""
        context = engine.build_narrative_context(
            audience=NarrativeAudience.GROWTH,
            **mock_system_components
        )

        assert context.audience == NarrativeAudience.GROWTH
        assert context.style == NarrativeStyle.INSPIRATIONAL

    def test_context_validation_success(self, engine, mock_system_components):
        """Test context validation with valid data."""
        context = engine.build_narrative_context(
            audience=NarrativeAudience.INVESTORS,
            **mock_system_components
        )

        assert engine.validate_narrative_context(context)

    def test_context_validation_missing_component(self, engine):
        """Test context validation with missing components."""
        incomplete_context = NarrativeContext(
            audience=NarrativeAudience.INVESTORS,
            style=NarrativeStyle.ANALYTICAL,
            phase=ConsciousnessPhase.GROWING,
            intent=None,  # Missing intent
            decision=None,
            frontier_health=0.5,
            culture_profile=None,
            environment_state=None
        )

        assert not engine.validate_narrative_context(incomplete_context)

    def test_context_validation_invalid_frontier_health(self, engine, mock_system_components):
        """Test context validation with invalid frontier health."""
        mock_system_components['frontier_health'] = 1.5  # Invalid value > 1.0

        context = engine.build_narrative_context(
            audience=NarrativeAudience.INVESTORS,
            **mock_system_components
        )

        assert not engine.validate_narrative_context(context)


class TestStyleSelection:
    """Test narrative style selection logic."""

    @pytest.fixture
    def engine(self):
        return NarrativeIntelligenceEngine()

    def test_style_mapping_completeness(self, engine):
        """Test that all audiences have style mappings."""
        for audience in NarrativeAudience:
            style = engine._select_style(audience)
            assert isinstance(style, NarrativeStyle)
            assert style in NarrativeStyle

    def test_investor_style_analytical(self, engine):
        """Test that investors get analytical style."""
        style = engine._select_style(NarrativeAudience.INVESTORS)
        assert style == NarrativeStyle.ANALYTICAL

    def test_employee_style_inspirational(self, engine):
        """Test that employees get inspirational style."""
        style = engine._select_style(NarrativeAudience.EMPLOYEES)
        assert style == NarrativeStyle.INSPIRATIONAL

    def test_crisis_style_transparent(self, engine):
        """Test that crisis situations get transparent style."""
        style = engine._select_style(NarrativeAudience.CRISIS)
        assert style == NarrativeStyle.TRANSPARENT

    def test_transformation_style_confident(self, engine):
        """Test that transformation gets confident style."""
        style = engine._select_style(NarrativeAudience.TRANSFORMATION)
        assert style == NarrativeStyle.CONFIDENT

    def test_growth_style_inspirational(self, engine):
        """Test that growth gets inspirational style."""
        style = engine._select_style(NarrativeAudience.GROWTH)
        assert style == NarrativeStyle.INSPIRATIONAL


class TestContextIntegration:
    """Test integration of context building with system components."""

    @pytest.fixture
    def engine(self):
        return NarrativeIntelligenceEngine()

    def test_context_preserves_component_data(self, engine):
        """Test that context building preserves all component data."""
        # Create comprehensive test data
        test_data = {
            'phase': ConsciousnessPhase.CONSOLIDATING,
            'intent': CorporateIntent(
                mission="Test mission",
                vision="Test vision",
                values=["Test value"]
            ),
            'decision': ExecutiveDecisionResult(
                selected_candidate_id="strategy_001",
                selected_candidate_desc="Approved strategic investment in R&D",
                votes=[],
                aggregated_score=0.85,
                method="weighted_average",
                vote_distribution={"strategy_001": 0.85},
                supporting_roles=["CEO", "CTO"],
                opposing_roles=[],
                all_scores={},
                timestamp=datetime.now()
            ),
            'frontier_health': 0.85,
            'culture_profile': CultureProfile(
                period="2024-01",
                aggressiveness_culture=0.5,
                risk_aversion_culture=0.5,
                brand_culture=0.5,
                cost_culture=0.5,
                people_culture=0.5,
                execution_culture=0.5,
                innovation_culture=0.5,
                stability_culture=0.5,
                notes="Balanced culture profile for test"
            ),
            'environment_state': ExternalEnvironmentState(
                period="2024-01",
                pest=PESTFactors(political=0.2, economic=0.3, social=0.3, technological=0.4),
                competitors=[],
                shocks=[],
                market_growth_modifier=1.0,
                risk_modifier=0.5
            )
        }

        context = engine.build_narrative_context(
            audience=NarrativeAudience.CUSTOMERS,
            **test_data
        )

        # Verify all data is preserved
        assert context.phase == test_data['phase']
        assert context.intent == test_data['intent']
        assert context.decision == test_data['decision']
        assert context.frontier_health == test_data['frontier_health']
        assert context.culture_profile == test_data['culture_profile']
        assert context.environment_state == test_data['environment_state']

    def test_context_handles_none_values_gracefully(self, engine):
        """Test that context building handles None values gracefully."""
        minimal_data = {
            'phase': ConsciousnessPhase.EMERGING,
            'intent': None,
            'decision': None,
            'frontier_health': 0.5,
            'culture_profile': None,
            'environment_state': None
        }

        context = engine.build_narrative_context(
            audience=NarrativeAudience.PUBLIC,
            **minimal_data
        )

        assert context.audience == NarrativeAudience.PUBLIC
        assert context.phase == ConsciousnessPhase.EMERGING
        assert context.intent is None
        assert context.decision is None
        assert context.frontier_health == 0.5
        assert context.culture_profile is None
        assert context.environment_state is None