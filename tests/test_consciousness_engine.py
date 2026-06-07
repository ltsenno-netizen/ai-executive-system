"""
Tests for Consciousness Engine (Step AE)

Tests the core logic for generating corporate consciousness:
- Self-assessment generation
- Identity, purpose, direction statements
- Meta-decision synthesis
- Quality metrics computation
"""

import pytest
from datetime import datetime
from src.backend.app.services.consciousness_engine import ConsciousnessEngine
from src.backend.app.models.corporate_consciousness_model import (
    CorporateConsciousness,
    ConsciousnessStatement,
    CorporateSelfModel,
)
from src.backend.app.models.corporate_intent_model import CorporateIntent
from src.backend.app.models.executive_agent_model import ExecutiveAgentConfig
from src.backend.app.models.culture_model import CultureProfile


@pytest.fixture
def consciousness_engine():
    """Create a consciousness engine instance"""
    return ConsciousnessEngine()


@pytest.fixture
def sample_intent():
    """Create sample corporate intent"""
    return CorporateIntent(
        period="2026-01",
        growth_weight=0.3,
        profitability_weight=0.3,
        innovation_weight=0.2,
        stability_weight=0.2,
        cultural_identity="innovative",
        strategic_priorities=["AI Integration", "Market Expansion"],
    )


@pytest.fixture
def sample_agents():
    """Create sample executive agents"""
    return [
        ExecutiveAgentConfig(
            role="Chief Strategy Officer",
            responsibilities=["Strategic Planning", "Market Analysis"],
            decision_authority=0.85,
            risk_tolerance=0.65,
        ),
        ExecutiveAgentConfig(
            role="Chief Technology Officer",
            responsibilities=["Innovation", "Technical Excellence"],
            decision_authority=0.75,
            risk_tolerance=0.7,
        ),
    ]


@pytest.fixture
def sample_culture():
    """Create sample culture profile"""
    return CultureProfile(
        period="2026-01",
        innovation_culture=0.75,
        people_culture=0.7,
        process_culture=0.65,
        market_culture=0.8,
        aggressiveness_culture=0.6,
        risk_aversion_culture=0.4,
        brand_culture=0.75,
        cost_culture=0.5,
        execution_culture=0.7,
        stability_culture=0.6,
    )


class TestConsciousnessEngineInitialization:
    """Test engine initialization"""

    def test_engine_initializes(self, consciousness_engine):
        """Test engine can be instantiated"""
        assert consciousness_engine is not None
        assert hasattr(consciousness_engine, "generate_corporate_consciousness")

    def test_engine_has_required_methods(self, consciousness_engine):
        """Test engine has all required methods"""
        required_methods = [
            "generate_corporate_consciousness",
            "_build_self_assessment",
            "_build_identity_statement",
            "_build_purpose_statement",
            "_build_strategic_direction",
            "_build_evolution_trajectory",
            "_build_meta_decision_synthesis",
            "_generate_consciousness_statement",
            "_compute_model_coherence",
            "_compute_authenticity_score",
        ]
        for method_name in required_methods:
            assert hasattr(consciousness_engine, method_name), f"Missing method: {method_name}"


class TestSelfAssessment:
    """Test self-assessment generation"""

    def test_self_assessment_has_dimensions(self, consciousness_engine, sample_intent, sample_culture):
        """Test self-assessment includes all required dimensions"""
        assessment = consciousness_engine._build_self_assessment(
            intent=sample_intent,
            frontier_health={"density": 0.7, "coverage": 0.8},
            culture=sample_culture,
            environment={"market_growth": 0.05},
        )
        
        assert assessment is not None
        assert assessment.overall_health > 0
        assert assessment.overall_health <= 1
        assert len(assessment.dimensions) == 6  # 6 dimensions
        assert assessment.maturity_level in ["startup", "growing", "established", "mature", "transforming"]

    def test_self_assessment_swot_generated(self, consciousness_engine, sample_intent, sample_culture):
        """Test SWOT analysis is generated"""
        assessment = consciousness_engine._build_self_assessment(
            intent=sample_intent,
            frontier_health={"density": 0.7, "coverage": 0.8},
            culture=sample_culture,
            environment={"market_growth": 0.05},
        )
        
        assert assessment.swot_analysis is not None
        assert "strengths" in assessment.swot_analysis
        assert "weaknesses" in assessment.swot_analysis
        assert "opportunities" in assessment.swot_analysis
        assert "threats" in assessment.swot_analysis


class TestIdentityStatement:
    """Test identity statement generation"""

    def test_identity_has_required_fields(self, consciousness_engine, sample_intent, sample_culture):
        """Test identity statement includes all required fields"""
        identity = consciousness_engine._build_identity_statement(
            intent=sample_intent,
            culture=sample_culture,
            company_history={"founding_year": 2010, "major_milestones": ["IPO 2015"]},
        )
        
        assert identity is not None
        assert len(identity.core_identity) > 0
        assert identity.cultural_archetype in ["innovator", "sage", "magician", "protector", "caregiver", "leader", "challenger"]
        assert len(identity.brand_promise) > 0
        assert len(identity.value_hierarchy) > 0
        assert 0 <= identity.identity_confidence <= 1


class TestPurposeStatement:
    """Test purpose statement generation"""

    def test_purpose_has_stakeholder_focus(self, consciousness_engine, sample_intent):
        """Test purpose statement addresses all stakeholders"""
        purpose = consciousness_engine._build_purpose_statement(
            intent=sample_intent,
            company_history={"founding_purpose": "Transform industries through innovation"},
        )
        
        assert purpose is not None
        assert len(purpose.mission) > 0
        assert len(purpose.vision) > 0
        assert purpose.stakeholder_purposes is not None
        assert "employees" in purpose.stakeholder_purposes
        assert "customers" in purpose.stakeholder_purposes
        assert "investors" in purpose.stakeholder_purposes
        assert "society" in purpose.stakeholder_purposes


class TestStrategicDirection:
    """Test strategic direction generation"""

    def test_direction_defines_strategy(self, consciousness_engine, sample_intent, sample_agents):
        """Test strategic direction is clearly defined"""
        direction = consciousness_engine._build_strategic_direction(
            intent=sample_intent,
            agents=sample_agents,
            frontier_health={"density": 0.7},
        )
        
        assert direction is not None
        assert len(direction.primary_strategy) > 0
        assert len(direction.strategic_focus_areas) > 0
        assert len(direction.key_priorities) > 0
        assert direction.risk_posture in ["risk-averse", "balanced", "aggressive"]
        assert 0 <= direction.innovation_intensity <= 1
        assert 0 <= direction.direction_confidence <= 1


class TestEvolutionTrajectory:
    """Test evolution trajectory generation"""

    def test_evolution_trajectory_set(self, consciousness_engine, sample_intent):
        """Test evolution trajectory is properly set"""
        trajectory = consciousness_engine._build_evolution_trajectory(
            intent=sample_intent,
            assessment={},
            company_history={},
        )
        
        assert trajectory is not None
        assert trajectory.current_phase_name is not None
        assert trajectory.next_phase_anticipated is not None
        assert -1 <= trajectory.evolutionary_momentum <= 1
        assert 0 <= trajectory.adaptability_index <= 1
        assert 0 <= trajectory.resilience_index <= 1


class TestMetaDecisionSynthesis:
    """Test meta-decision synthesis"""

    def test_meta_synthesis_integrates_sources(self, consciousness_engine, sample_intent, sample_agents):
        """Test meta-decision synthesizes all sources"""
        synthesis = consciousness_engine._build_meta_decision_synthesis(
            intent=sample_intent,
            agents=sample_agents,
            frontier_health={"density": 0.7},
            culture={"innovation": 0.75},
            company_history={"major_shifts": 3},
            environment={"market_volatility": 0.6},
        )
        
        assert synthesis is not None
        assert synthesis.intent_contribution is not None
        assert synthesis.agent_contribution is not None
        assert synthesis.frontier_contribution is not None
        assert 0 <= synthesis.consensus_level <= 1
        assert len(synthesis.unified_direction) > 0


class TestQualityMetrics:
    """Test quality metric computation"""

    def test_authenticity_score_computed(self, consciousness_engine):
        """Test authenticity score is computed"""
        score = consciousness_engine._compute_authenticity_score(
            identity_confidence=0.8,
            purpose_clarity=0.85,
            direction_confidence=0.75,
        )
        assert 0 <= score <= 1

    def test_model_coherence_computed(self, consciousness_engine):
        """Test model coherence is computed"""
        score = consciousness_engine._compute_model_coherence(
            {
                "identity_confidence": 0.8,
                "purpose_clarity": 0.85,
                "direction_confidence": 0.75,
                "alignment_score": 0.82,
            }
        )
        assert 0 <= score <= 1


class TestConsciousnessGeneration:
    """Test end-to-end consciousness generation"""

    def test_full_consciousness_generated(
        self, consciousness_engine, sample_intent, sample_agents, sample_culture
    ):
        """Test complete consciousness can be generated"""
        consciousness = consciousness_engine.generate_corporate_consciousness(
            intent=sample_intent,
            agents=sample_agents,
            frontier_analysis=None,
            frontier_health={"density": 0.7, "coverage": 0.8},
            culture=sample_culture,
            company_history={"founding_year": 2010},
            environment={"market_growth": 0.05},
            current_cycle=None,
            period="2026-01",
            company_name="TechCorp",
        )
        
        assert consciousness is not None
        assert isinstance(consciousness, CorporateConsciousness)
        assert consciousness.overall_consciousness_score > 0
        assert consciousness.identity_statement is not None
        assert consciousness.purpose_statement is not None
        assert consciousness.strategic_direction is not None

    def test_consciousness_statement_generated(
        self, consciousness_engine, sample_intent, sample_agents, sample_culture
    ):
        """Test consciousness statement narratives are generated"""
        consciousness = consciousness_engine.generate_corporate_consciousness(
            intent=sample_intent,
            agents=sample_agents,
            frontier_analysis=None,
            frontier_health={"density": 0.7, "coverage": 0.8},
            culture=sample_culture,
            company_history={},
            environment={},
            current_cycle=None,
            period="2026-01",
            company_name="TechCorp",
        )
        
        # Check consciousness statement
        assert consciousness.consciousness_statement is not None
        assert isinstance(consciousness.consciousness_statement, ConsciousnessStatement)
        assert len(consciousness.consciousness_statement.identity_narrative) > 0
        assert len(consciousness.consciousness_statement.purpose_narrative) > 0
        assert len(consciousness.consciousness_statement.direction_narrative) > 0
        assert len(consciousness.consciousness_statement.identity_one_liner) > 0
        assert len(consciousness.consciousness_statement.identity_one_liner) <= 140  # One-liner constraint


class TestConsciousnessIntegration:
    """Test consciousness integration with other components"""

    def test_consciousness_references_intent(self, consciousness_engine, sample_intent):
        """Test consciousness incorporates intent"""
        consciousness = consciousness_engine.generate_corporate_consciousness(
            intent=sample_intent,
            agents=[],
            frontier_analysis=None,
            frontier_health={},
            culture=None,
            company_history={},
            environment={},
            current_cycle=None,
            period="2026-01",
            company_name="TestCorp",
        )
        
        # Consciousness should reflect intent priorities
        assert consciousness is not None
        assert consciousness.self_model.meta_decision_synthesis.intent_contribution is not None

    def test_consciousness_reflects_culture(self, consciousness_engine, sample_intent, sample_culture):
        """Test consciousness reflects cultural values"""
        consciousness = consciousness_engine.generate_corporate_consciousness(
            intent=sample_intent,
            agents=[],
            frontier_analysis=None,
            frontier_health={},
            culture=sample_culture,
            company_history={},
            environment={},
            current_cycle=None,
            period="2026-01",
            company_name="TestCorp",
        )
        
        assert consciousness is not None
        # Consciousness should incorporate culture
        assert consciousness.self_model.identity_statement.cultural_archetype is not None
