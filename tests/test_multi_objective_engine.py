import pytest
from src.backend.app.services.multi_objective_engine import (
    compute_objective_vector,
    dominates,
    build_pareto_frontier,
)
from src.backend.app.models.scenario_model import ScenarioResult, ScenarioType
from src.backend.app.models.self_optimization_model import SelfOptimizationPlan, OptimizationObjective
from src.backend.app.models.multi_objective_model import ObjectiveVector, StrategyCandidate
from src.backend.app.models.strategy_model import StrategyHorizon, StrategyRiskLevel


def test_compute_objective_vector():
    """Test computing objective vector from scenario and plan"""
    scenario = ScenarioResult(
        scenario_type=ScenarioType.OPTIMISTIC,
        projected_culture=None,
        projected_executive_team=None,
        projected_financials={"revenue": 130.0, "profit": 13.0, "cash": 65.0},
        projected_evolution_score=0.75,
        risk_assessment="Low",
        opportunity_assessment="High"
    )
    
    plan = SelfOptimizationPlan(
        objective=OptimizationObjective.GROWTH,
        selected_scenario=ScenarioType.OPTIMISTIC,
        recommended_strategies=[],
        recommended_culture_shifts=[],
        recommended_leadership_changes=[],
        expected_evolution_score=0.75
    )
    
    vector = compute_objective_vector(scenario, plan)
    
    assert vector.growth == 130.0
    assert vector.profitability == 13.0
    assert vector.innovation == 0.75
    assert vector.stability > 0.0


def test_dominates():
    """Test Pareto dominance check"""
    vector_a = ObjectiveVector(growth=100, profitability=10, innovation=0.8, stability=0.8)
    vector_b = ObjectiveVector(growth=90, profitability=9, innovation=0.7, stability=0.7)
    vector_c = ObjectiveVector(growth=100, profitability=8, innovation=0.8, stability=0.8)
    
    # A dominates B
    assert dominates(vector_a, vector_b)
    
    # A does not dominate C (C has lower profit but same growth/innovation/stability)
    assert not dominates(vector_a, vector_c)
    
    # B does not dominate A
    assert not dominates(vector_b, vector_a)


def test_build_pareto_frontier():
    """Test Pareto frontier construction"""
    candidates = [
        StrategyCandidate(
            scenario_type=ScenarioType.OPTIMISTIC,
            optimization_objective=OptimizationObjective.GROWTH,
            scenario_summary="High growth strategy",
            objective_vector=ObjectiveVector(growth=140, profitability=12, innovation=0.75, stability=0.7),
            roadmap_title="Growth Focus",
            strategy_count=5,
            key_focus="Growth",
        ),
        StrategyCandidate(
            scenario_type=ScenarioType.BASELINE,
            optimization_objective=OptimizationObjective.STABILITY,
            scenario_summary="Stable strategy",
            objective_vector=ObjectiveVector(growth=100, profitability=15, innovation=0.6, stability=0.9),
            roadmap_title="Stability Focus",
            strategy_count=3,
            key_focus="Stability",
        ),
        StrategyCandidate(
            scenario_type=ScenarioType.OPTIMISTIC,
            optimization_objective=OptimizationObjective.INNOVATION,
            scenario_summary="Innovation strategy",
            objective_vector=ObjectiveVector(growth=120, profitability=11, innovation=0.85, stability=0.75),
            roadmap_title="Innovation Focus",
            strategy_count=6,
            key_focus="Innovation",
        ),
    ]
    
    frontier = build_pareto_frontier(candidates)
    
    assert frontier.total_candidates == 3
    assert frontier.frontier_count >= 2  # At least 2 non-dominated
    assert len(frontier.frontier_indices) == frontier.frontier_count
