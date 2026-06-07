import pytest
from src.backend.app.services.strategy_application_engine import (
    apply_strategy_roadmap_to_state,
    calculate_strategy_effectiveness,
)
from src.backend.app.models.strategy_model import (
    StrategyRoadmap,
    StrategyItem,
    StrategyHorizon,
    StrategyRiskLevel,
)
from src.backend.app.models.self_optimization_model import OptimizationObjective
from src.backend.app.models.scenario_model import ScenarioType
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.ai_ceo_model import AICeoPersona
from src.backend.app.models.external_environment_model_v2 import ExternalEnvironmentState, PESTFactors
from src.backend.app.models.enterprise_evolution_model import EnterpriseEvolutionResult


def test_apply_strategy_roadmap_to_culture():
    """Test applying strategies to culture"""
    roadmap = StrategyRoadmap(
        objective=OptimizationObjective.GROWTH,
        selected_scenario=ScenarioType.OPTIMISTIC,
        key_focus="成長ドライバーの最大化",
        strategies=[
            StrategyItem(
                title="新規事業投資",
                description="テック企業との協業",
                horizon=StrategyHorizon.MID_TERM,
                priority=1,
                expected_impact=0.8,
                risk_level=StrategyRiskLevel.MEDIUM,
            )
        ],
    )
    
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
        stability_culture=0.5,
    )
    
    executive_team = {"CEO": AICeoPersona(aggressiveness=0.5, risk_tolerance=0.5, brand_priority=0.5, short_term_focus=0.5, long_term_focus=0.5)}
    environment = ExternalEnvironmentState(period="2026-04", pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.6), competitors=[], shocks=[])
    evolution = EnterpriseEvolutionResult(evolution_score=0.65, environment_pressure=0.5, culture_shift={}, leadership_shift={})
    
    new_culture, new_team, new_env, new_evolution, details = apply_strategy_roadmap_to_state(
        roadmap, culture, executive_team, environment, evolution
    )
    
    # Culture should change
    assert new_culture.innovation_culture > culture.innovation_culture
    assert new_evolution.evolution_score >= evolution.evolution_score


def test_calculate_strategy_effectiveness():
    """Test calculating strategy effectiveness"""
    effectiveness = calculate_strategy_effectiveness(0.65, 0.72, 3)
    
    # Effectiveness should be positive
    assert effectiveness > 0.0
    assert effectiveness == (0.72 - 0.65) / 3
