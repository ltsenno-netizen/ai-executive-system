import pytest
from src.backend.app.services.corporate_story_engine import (
    build_history_section,
    build_current_state_section,
    build_scenario_section,
    build_optimization_section,
    generate_corporate_story
)
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.external_environment_model_v2 import ExternalEnvironmentState, PESTFactors
from src.backend.app.models.ai_ceo_model import AICeoPersona
from src.backend.app.models.enterprise_evolution_model import EnterpriseEvolutionResult
from src.backend.app.models.scenario_model import ScenarioType, ScenarioResult
from src.backend.app.models.self_optimization_model import OptimizationObjective, SelfOptimizationPlan


def test_build_history_section():
    """Test history section generation"""
    history = {
        "major_events": ["CEO change 2025", "M&A 2024"],
        "culture_trends": {"innovation_culture": 0.6},
        "evolution_trend": 0.65
    }
    
    section = build_history_section(history)
    
    assert section.title == "企業の歩み"
    assert "リーダーシップ転換" in section.content
    assert "進化スコア" in section.content


def test_build_current_state_section():
    """Test current state section generation"""
    culture = CultureProfile(
        period="2026-04",
        innovation_culture=0.6,
        people_culture=0.5,
        process_culture=0.5,
        market_culture=0.5,
        aggressiveness_culture=0.5,
        risk_aversion_culture=0.5,
        brand_culture=0.5,
        cost_culture=0.5,
        execution_culture=0.5,
        stability_culture=0.5
    )
    environment = ExternalEnvironmentState(
        period="2026-04",
        pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.6),
        competitors=[],
        shocks=[]
    )
    executive_team = {
        "CEO": AICeoPersona(aggressiveness=0.5, risk_tolerance=0.5, brand_priority=0.5, short_term_focus=0.5, long_term_focus=0.5)
    }
    evolution = EnterpriseEvolutionResult(
        evolution_score=0.65,
        environment_pressure=0.5,
        culture_shift={},
        leadership_shift={}
    )
    
    section = build_current_state_section(culture, environment, executive_team, evolution)
    
    assert section.title == "現在の姿"
    assert "組織文化" in section.content
    assert "経営チーム" in section.content


def test_build_scenario_section():
    """Test scenario section generation"""
    scenarios = [
        ScenarioResult(
            scenario_type=ScenarioType.OPTIMISTIC,
            projected_culture=CultureProfile(period="2026-04", innovation_culture=0.7, people_culture=0.5, process_culture=0.5, market_culture=0.5, aggressiveness_culture=0.6, risk_aversion_culture=0.4, brand_culture=0.5, cost_culture=0.5, execution_culture=0.5, stability_culture=0.5),
            projected_executive_team={"CEO": AICeoPersona(aggressiveness=0.6, risk_tolerance=0.6, brand_priority=0.5, short_term_focus=0.5, long_term_focus=0.5)},
            projected_financials={"revenue": 130.0, "profit": 13.0, "cash": 65.0},
            projected_evolution_score=0.75,
            risk_assessment="Low",
            opportunity_assessment="High"
        )
    ]
    
    section = build_scenario_section(scenarios)
    
    assert section.title == "未来の可能性"
    assert "OPTIMISTIC" in section.content


def test_generate_corporate_story():
    """Test complete story generation"""
    history = {
        "major_events": ["CEO change"],
        "culture_trends": {},
        "evolution_trend": 0.65
    }
    culture = CultureProfile(
        period="2026-04",
        innovation_culture=0.6,
        people_culture=0.5,
        process_culture=0.5,
        market_culture=0.5,
        aggressiveness_culture=0.5,
        risk_aversion_culture=0.5,
        brand_culture=0.5,
        cost_culture=0.5,
        execution_culture=0.5,
        stability_culture=0.5
    )
    environment = ExternalEnvironmentState(
        period="2026-04",
        pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.6),
        competitors=[],
        shocks=[]
    )
    team = {"CEO": AICeoPersona(aggressiveness=0.5, risk_tolerance=0.5, brand_priority=0.5, short_term_focus=0.5, long_term_focus=0.5)}
    evolution = EnterpriseEvolutionResult(evolution_score=0.65, environment_pressure=0.5, culture_shift={}, leadership_shift={})
    scenarios = []
    plan = SelfOptimizationPlan(
        objective=OptimizationObjective.GROWTH,
        selected_scenario=ScenarioType.BASELINE,
        recommended_strategies=[],
        recommended_culture_shifts=[],
        recommended_leadership_changes=[],
        expected_evolution_score=0.65
    )
    
    story = generate_corporate_story("2026-04", history, culture, environment, team, evolution, scenarios, plan)
    
    assert story.period == "2026-04"
    assert len(story.sections) == 5
    assert story.summary is not None
