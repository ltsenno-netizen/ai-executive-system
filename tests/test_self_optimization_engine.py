import pytest
from src.backend.app.services.self_optimization_engine import (
    select_best_scenario,
    build_strategy_adjustments,
    build_culture_adjustments,
    build_leadership_adjustments,
    build_self_optimization_plan
)
from src.backend.app.models.self_optimization_model import OptimizationObjective
from src.backend.app.models.scenario_model import ScenarioType, ScenarioResult
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.ai_ceo_model import AICeoPersona


def test_select_best_scenario_for_growth():
    """Test scenario selection for GROWTH objective"""
    scenarios = [
        ScenarioResult(
            scenario_type=ScenarioType.BASELINE,
            projected_culture=CultureProfile(period="2026-04", innovation_culture=0.5, people_culture=0.5, process_culture=0.5, market_culture=0.5, aggressiveness_culture=0.5, risk_aversion_culture=0.5, brand_culture=0.5, cost_culture=0.5, execution_culture=0.5, stability_culture=0.5),
            projected_executive_team={"CEO": AICeoPersona(aggressiveness=0.5, risk_tolerance=0.5, brand_priority=0.5, short_term_focus=0.5, long_term_focus=0.5)},
            projected_financials={"revenue": 110.0, "profit": 11.0, "cash": 55.0},
            projected_evolution_score=0.5,
            risk_assessment="Medium",
            opportunity_assessment="Medium"
        ),
        ScenarioResult(
            scenario_type=ScenarioType.OPTIMISTIC,
            projected_culture=CultureProfile(period="2026-04", innovation_culture=0.6, people_culture=0.5, process_culture=0.5, market_culture=0.5, aggressiveness_culture=0.6, risk_aversion_culture=0.4, brand_culture=0.5, cost_culture=0.5, execution_culture=0.5, stability_culture=0.5),
            projected_executive_team={"CEO": AICeoPersona(aggressiveness=0.6, risk_tolerance=0.6, brand_priority=0.5, short_term_focus=0.5, long_term_focus=0.5)},
            projected_financials={"revenue": 130.0, "profit": 13.0, "cash": 65.0},
            projected_evolution_score=0.6,
            risk_assessment="Low",
            opportunity_assessment="High"
        )
    ]
    
    best = select_best_scenario(OptimizationObjective.GROWTH, scenarios)
    assert best.scenario_type == ScenarioType.OPTIMISTIC
    assert best.projected_financials["revenue"] == 130.0


def test_select_best_scenario_for_innovation():
    """Test scenario selection for INNOVATION objective"""
    scenarios = [
        ScenarioResult(
            scenario_type=ScenarioType.BASELINE,
            projected_culture=CultureProfile(period="2026-04", innovation_culture=0.5, people_culture=0.5, process_culture=0.5, market_culture=0.5, aggressiveness_culture=0.5, risk_aversion_culture=0.5, brand_culture=0.5, cost_culture=0.5, execution_culture=0.5, stability_culture=0.5),
            projected_executive_team={"CEO": AICeoPersona(aggressiveness=0.5, risk_tolerance=0.5, brand_priority=0.5, short_term_focus=0.5, long_term_focus=0.5)},
            projected_financials={"revenue": 110.0, "profit": 11.0, "cash": 55.0},
            projected_evolution_score=0.5,
            risk_assessment="Medium",
            opportunity_assessment="Medium"
        ),
        ScenarioResult(
            scenario_type=ScenarioType.TECH_BOOM,
            projected_culture=CultureProfile(period="2026-04", innovation_culture=0.7, people_culture=0.5, process_culture=0.5, market_culture=0.5, aggressiveness_culture=0.6, risk_aversion_culture=0.4, brand_culture=0.5, cost_culture=0.5, execution_culture=0.5, stability_culture=0.5),
            projected_executive_team={"CEO": AICeoPersona(aggressiveness=0.6, risk_tolerance=0.6, brand_priority=0.5, short_term_focus=0.5, long_term_focus=0.5)},
            projected_financials={"revenue": 120.0, "profit": 12.0, "cash": 60.0},
            projected_evolution_score=0.8,
            risk_assessment="Medium",
            opportunity_assessment="High"
        )
    ]
    
    best = select_best_scenario(OptimizationObjective.INNOVATION, scenarios)
    assert best.scenario_type == ScenarioType.TECH_BOOM
    assert best.projected_evolution_score == 0.8


def test_build_strategy_adjustments():
    """Test strategy adjustment building"""
    scenario = ScenarioResult(
        scenario_type=ScenarioType.BASELINE,
        projected_culture=CultureProfile(period="2026-04", innovation_culture=0.5, people_culture=0.5, process_culture=0.5, market_culture=0.5, aggressiveness_culture=0.5, risk_aversion_culture=0.5, brand_culture=0.5, cost_culture=0.5, execution_culture=0.5, stability_culture=0.5),
        projected_executive_team={"CEO": AICeoPersona(aggressiveness=0.5, risk_tolerance=0.5, brand_priority=0.5, short_term_focus=0.5, long_term_focus=0.5)},
        projected_financials={"revenue": 100.0, "profit": 9.0, "cash": 50.0},
        projected_evolution_score=0.4,
        risk_assessment="Medium",
        opportunity_assessment="Medium"
    )
    current_financials = {"revenue": 100.0, "profit": 10.0, "cash": 50.0}
    
    adjustments = build_strategy_adjustments(scenario, current_financials)
    
    assert len(adjustments) > 0
    assert any(a.description == "コスト構造の見直し" for a in adjustments)


def test_build_culture_adjustments():
    """Test culture adjustment building"""
    scenario = ScenarioResult(
        scenario_type=ScenarioType.TECH_BOOM,
        projected_culture=CultureProfile(period="2026-04", innovation_culture=0.6, people_culture=0.5, process_culture=0.5, market_culture=0.5, aggressiveness_culture=0.5, risk_aversion_culture=0.5, brand_culture=0.5, cost_culture=0.5, execution_culture=0.5, stability_culture=0.5),
        projected_executive_team={"CEO": AICeoPersona(aggressiveness=0.5, risk_tolerance=0.5, brand_priority=0.5, short_term_focus=0.5, long_term_focus=0.5)},
        projected_financials={"revenue": 120.0, "profit": 12.0, "cash": 60.0},
        projected_evolution_score=0.8,
        risk_assessment="Medium",
        opportunity_assessment="High"
    )
    current_culture = CultureProfile(period="2026-04", innovation_culture=0.5, people_culture=0.5, process_culture=0.5, market_culture=0.5, aggressiveness_culture=0.5, risk_aversion_culture=0.5, brand_culture=0.5, cost_culture=0.5, execution_culture=0.5, stability_culture=0.5)
    
    adjustments = build_culture_adjustments(scenario, current_culture)
    
    assert any(a.dimension == "innovation_culture" and a.delta == 0.1 for a in adjustments)
