"""
Tests for Narrative Generation Engine
====================================

Tests for the core narrative generation engine that composes narratives
based on context and audience requirements.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from src.backend.app.services.narrative_intelligence_engine import NarrativeIntelligenceEngine
from src.backend.app.models.narrative_intelligence_model import (
    GeneratedNarrative,
    NarrativeAudience,
    NarrativeContext,
    NarrativeStyle,
)
from src.backend.app.models.corporate_consciousness_evolution_model import ConsciousnessPhase
from src.backend.app.models.corporate_intent_model import CorporateIntent
from src.backend.app.models.executive_agent_model import ExecutiveDecisionResult
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.external_environment_model_v2 import ExternalEnvironmentState, PESTFactors


class TestNarrativeGenerationEngine:
    """Test narrative generation engine functionality."""

    @pytest.fixture
    def engine(self):
        """Create narrative intelligence engine instance."""
        return NarrativeIntelligenceEngine()

    @pytest.fixture
    def sample_context(self):
        """Create a sample narrative context for testing."""
        return NarrativeContext(
            audience=NarrativeAudience.INVESTORS,
            style=NarrativeStyle.ANALYTICAL,
            phase=ConsciousnessPhase.GROWING,
            intent=CorporateIntent(
                mission="To create sustainable value through innovation",
                vision="Leading the industry in sustainable technology",
                values=["Innovation", "Sustainability", "Excellence"]
            ),
            decision=ExecutiveDecisionResult(
                selected_candidate_id="strategy_001",
                selected_candidate_desc="Approved $50M investment in green technology",
                votes=[],
                aggregated_score=0.9,
                method="weighted_average",
                vote_distribution={"strategy_001": 0.9},
                supporting_roles=["CEO", "CTO"],
                opposing_roles=[],
                all_scores={},
                timestamp=datetime.now()
            ),
            frontier_health=0.8,
            culture_profile=CultureProfile(
                period="2024-01",
                aggressiveness_culture=0.6,
                risk_aversion_culture=0.4,
                brand_culture=0.8,
                cost_culture=0.5,
                people_culture=0.7,
                execution_culture=0.75,
                innovation_culture=0.8,
                stability_culture=0.6,
                notes="Dynamic culture supporting innovation"
            ),
            environment_state=ExternalEnvironmentState(
                period="2024-01",
                pest=PESTFactors(political=0.3, economic=0.4, social=0.5, technological=0.7),
                competitors=[],
                shocks=[],
                market_growth_modifier=1.0,
                risk_modifier=0.8
            )
        )

    def test_generate_narrative_returns_valid_object(self, engine, sample_context):
        """Test that generate_narrative returns a valid GeneratedNarrative object."""
        narrative = engine.generate_narrative(sample_context)

        assert isinstance(narrative, GeneratedNarrative)
        assert narrative.audience == sample_context.audience
        assert narrative.style == sample_context.style
        assert isinstance(narrative.text, str)
        assert len(narrative.text) > 0
        assert isinstance(narrative.key_messages, list)
        assert isinstance(narrative.tone_markers, list)
        assert narrative.narrative_id is not None

    def test_generate_narrative_includes_phase_framing(self, engine, sample_context):
        """Test that generated narrative includes phase-based framing."""
        narrative = engine.generate_narrative(sample_context)

        # GROWING phase should mention growth/learning
        assert "growing" in narrative.text.lower() or "learning" in narrative.text.lower()

    def test_generate_narrative_includes_intent(self, engine, sample_context):
        """Test that generated narrative includes corporate intent."""
        narrative = engine.generate_narrative(sample_context)

        assert "sustainable value" in narrative.text.lower()
        assert "innovation" in narrative.text.lower()

    def test_generate_narrative_includes_decision(self, engine, sample_context):
        """Test that generated narrative includes executive decision."""
        narrative = engine.generate_narrative(sample_context)

        assert "investment" in narrative.text.lower() or "approved" in narrative.text.lower()

    def test_generate_narrative_includes_frontier_health(self, engine, sample_context):
        """Test that generated narrative includes frontier health interpretation."""
        narrative = engine.generate_narrative(sample_context)

        # High frontier health should mention exploration/optimization
        assert "optimization" in narrative.text.lower() or "exploration" in narrative.text.lower()

    def test_generate_narrative_includes_culture_environment(self, engine, sample_context):
        """Test that generated narrative includes culture and environment reflection."""
        narrative = engine.generate_narrative(sample_context)

        # Should mention culture momentum or environment
        culture_env_keywords = ["culture", "environment", "dynamic", "competitive", "sustainability"]
        assert any(keyword in narrative.text.lower() for keyword in culture_env_keywords)

    def test_generate_narrative_audience_specific_tone(self, engine, sample_context):
        """Test that generated narrative includes audience-specific tone."""
        narrative = engine.generate_narrative(sample_context)

        # Investor narrative should be analytical/professional
        investor_keywords = ["committed", "sustainable", "value", "growth"]
        assert any(keyword in narrative.text.lower() for keyword in investor_keywords)

    def test_key_messages_extraction(self, engine, sample_context):
        """Test that key messages are properly extracted."""
        narrative = engine.generate_narrative(sample_context)

        assert len(narrative.key_messages) > 0
        assert all(isinstance(msg, str) for msg in narrative.key_messages)
        assert all(len(msg) > 10 for msg in narrative.key_messages)  # Reasonable length

    def test_tone_markers_detection(self, engine, sample_context):
        """Test that tone markers are properly detected."""
        narrative = engine.generate_narrative(sample_context)

        assert len(narrative.tone_markers) > 0
        assert all(isinstance(marker, str) for marker in narrative.tone_markers)

        # Should detect analytical tone for investors
        assert "analytical" in narrative.tone_markers

    def test_different_audiences_produce_different_content(self, engine):
        """Test that different audiences produce different narrative content."""
        base_context = NarrativeContext(
            audience=NarrativeAudience.INVESTORS,  # Will be overridden
            style=NarrativeStyle.ANALYTICAL,
            phase=ConsciousnessPhase.CONSOLIDATING,
            intent=CorporateIntent(mission="Test mission", vision="Test vision", values=["Test"]),
            decision=ExecutiveDecisionResult(decision_summary="Test decision"),
            frontier_health=0.7,
            culture_profile=CultureProfile(
                period="2024-01",
                aggressiveness_culture=0.5, risk_aversion_culture=0.5, brand_culture=0.5,
                cost_culture=0.5, people_culture=0.5, execution_culture=0.5,
                innovation_culture=0.5, stability_culture=0.5,
                notes="Balanced culture profile for test"
            ),
            environment_state=ExternalEnvironmentState(
                period="2024-01",
                pest=PESTFactors(political=0.3, economic=0.3, social=0.2, technological=0.2),
                competitors=[],
                shocks=[],
                market_growth_modifier=1.0,
                risk_modifier=0.5
            )
        )

        narratives = {}
        for audience in [NarrativeAudience.INVESTORS, NarrativeAudience.EMPLOYEES, NarrativeAudience.CUSTOMERS]:
            context = base_context.copy()
            context.audience = audience
            context.style = engine._select_style(audience)
            narratives[audience] = engine.generate_narrative(context)

        # Different audiences should produce different content
        investor_text = narratives[NarrativeAudience.INVESTORS].text
        employee_text = narratives[NarrativeAudience.EMPLOYEES].text
        customer_text = narratives[NarrativeAudience.CUSTOMERS].text

        assert investor_text != employee_text
        assert investor_text != customer_text
        assert employee_text != customer_text

    def test_phase_specific_content(self, engine):
        """Test that different phases produce different content."""
        base_context = NarrativeContext(
            audience=NarrativeAudience.PUBLIC,
            style=NarrativeStyle.FORMAL,
            phase=ConsciousnessPhase.EMERGING,  # Will be overridden
            intent=CorporateIntent(mission="Test mission"),
            decision=ExecutiveDecisionResult(decision_summary="Test decision"),
            frontier_health=0.6,
            culture_profile=CultureProfile(
                period="2024-01",
                aggressiveness_culture=0.5, risk_aversion_culture=0.5, brand_culture=0.5,
                cost_culture=0.5, people_culture=0.5, execution_culture=0.5,
                innovation_culture=0.5, stability_culture=0.5,
                notes="Balanced culture profile for test"
            ),
            environment_state=ExternalEnvironmentState(
                period="2024-01",
                pest=PESTFactors(political=0.2, economic=0.2, social=0.2, technological=0.2),
                competitors=[],
                shocks=[],
                market_growth_modifier=1.0,
                risk_modifier=0.4
            )
        )

        phase_texts = {}
        for phase in [ConsciousnessPhase.EMERGING, ConsciousnessPhase.GROWING, ConsciousnessPhase.CONSOLIDATING]:
            context = base_context.copy()
            context.phase = phase
            narrative = engine.generate_narrative(context)
            phase_texts[phase] = narrative.text

        # Different phases should produce different framing
        assert phase_texts[ConsciousnessPhase.EMERGING] != phase_texts[ConsciousnessPhase.GROWING]
        assert phase_texts[ConsciousnessPhase.GROWING] != phase_texts[ConsciousnessPhase.CONSOLIDATING]

    def test_frontier_health_interpretation(self, engine):
        """Test that frontier health is properly interpreted in narratives."""
        base_context = NarrativeContext(
            audience=NarrativeAudience.PARTNERS,
            style=NarrativeStyle.TRANSPARENT,
            phase=ConsciousnessPhase.CONSOLIDATING,
            intent=CorporateIntent(mission="Test mission"),
            decision=ExecutiveDecisionResult(decision_summary="Test decision"),
            frontier_health=0.9,  # Will be overridden
            culture_profile=CultureProfile(
                period="2024-01",
                aggressiveness_culture=0.5, risk_aversion_culture=0.5, brand_culture=0.5,
                cost_culture=0.5, people_culture=0.5, execution_culture=0.5,
                innovation_culture=0.5, stability_culture=0.5,
                notes="Balanced culture profile for test"
            ),
            environment_state=ExternalEnvironmentState(
                period="2024-01",
                pest=PESTFactors(political=0.3, economic=0.3, social=0.3, technological=0.3),
                competitors=[],
                shocks=[],
                market_growth_modifier=1.0,
                risk_modifier=0.4
            )
        )

        # High frontier health
        context_high = base_context.copy()
        context_high.frontier_health = 0.9
        narrative_high = engine.generate_narrative(context_high)

        # Low frontier health
        context_low = base_context.copy()
        context_low.frontier_health = 0.3
        narrative_low = engine.generate_narrative(context_low)

        # Different frontier health should produce different content
        assert narrative_high.text != narrative_low.text

        # High health should mention exploration/optimization
        assert "optimization" in narrative_high.text.lower() or "exploration" in narrative_high.text.lower()

        # Low health should mention challenges/improvement
        assert "challeng" in narrative_low.text.lower() or "improv" in narrative_low.text.lower() or "addressing" in narrative_low.text.lower()

class TestNarrativeComposition:
    """Test narrative composition logic."""

    @pytest.fixture
    def engine(self):
        return NarrativeIntelligenceEngine()

    def test_compose_narrative_text_structure(self, engine):
        """Test that composed narrative has proper structure."""
        context = NarrativeContext(
            audience=NarrativeAudience.CUSTOMERS,
            style=NarrativeStyle.CONFIDENT,
            phase=ConsciousnessPhase.MATURING,
            intent=CorporateIntent(mission="To serve customers excellently"),
            decision=ExecutiveDecisionResult(decision_summary="Enhanced customer service"),
            frontier_health=0.7,
            culture_profile=CultureProfile(
                period="2024-01",
                aggressiveness_culture=0.5, risk_aversion_culture=0.5, brand_culture=0.5,
                cost_culture=0.5, people_culture=0.5, execution_culture=0.5,
                innovation_culture=0.5, stability_culture=0.5,
                notes="Balanced culture profile for test"
            ),
            environment_state=ExternalEnvironmentState(
                period="2024-01",
                pest=PESTFactors(political=0.1, economic=0.2, social=0.2, technological=0.3),
                competitors=[],
                shocks=[],
                market_growth_modifier=1.0,
                risk_modifier=0.1
            )
        )

        text = engine._compose_narrative_text(context)

        # Should have multiple paragraphs (separated by double newlines)
        paragraphs = text.split('\n\n')
        assert len(paragraphs) >= 3  # At least phase, intent, and conclusion

        # Should contain key elements
        assert len(text) > 100  # Reasonable length
        assert "matur" in text.lower()  # Both "maturing" and "maturity" contain "matur"
        assert "customers" in text.lower() or "serve" in text.lower()

    def test_extract_key_messages_logic(self, engine):
        """Test key message extraction logic."""
        test_text = """
        We are committed to sustainable growth and innovation.
        Our investment in green technology demonstrates our dedication to the environment.
        Together, we will build a better future for all stakeholders.
        The data shows strong performance in key markets.
        """

        messages = engine._extract_key_messages(test_text)

        assert len(messages) > 0
        assert all(isinstance(msg, str) for msg in messages)
        # Should extract meaningful sentences
        assert any("committed" in msg.lower() for msg in messages)
        assert any("investment" in msg.lower() for msg in messages)

    def test_detect_tone_markers_logic(self, engine):
        """Test tone marker detection logic."""
        test_text = """
        We are confident in our strategic direction and committed to delivering value.
        Our analytical approach ensures data-driven decisions.
        We remain transparent about challenges and opportunities.
        """

        markers = engine._detect_tone_markers(test_text)

        assert len(markers) > 0
        assert "confident" in markers
        assert "analytical" in markers
        assert "transparent" in markers