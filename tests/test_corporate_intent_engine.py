import pytest
from src.backend.app.services.corporate_intent_engine import (
    score_candidate,
    select_strategy_by_intent,
    calculate_intent_alignment,
    update_intent_from_history,
    apply_learning_to_intent,
)
from src.backend.app.models.corporate_intent_model import CorporateIntent
from src.backend.app.models.multi_objective_model import ObjectiveVector, StrategyCandidate
from src.backend.app.models.scenario_model import ScenarioType
from src.backend.app.models.self_optimization_model import OptimizationObjective


def test_score_candidate_growth_focused():
    """Test scoring with growth-focused intent"""
    intent = CorporateIntent(
        growth_weight=0.5,
        profitability_weight=0.2,
        innovation_weight=0.15,
        stability_weight=0.15,
        risk_preference=0.7,
        time_horizon=0.3,
    )
    
    candidate = StrategyCandidate(
        scenario_type=ScenarioType.OPTIMISTIC,
        optimization_objective=OptimizationObjective.GROWTH,
        scenario_summary="High growth strategy",
        objective_vector=ObjectiveVector(growth=140, profitability=12, innovation=0.7, stability=0.6),
        roadmap_title="Growth Focus",
        strategy_count=8,
        key_focus="成長ドライバー最大化",
    )
    
    score = score_candidate(intent, candidate)
    
    assert score.score > 0
    assert score.growth_component > 0
    assert score.breakdown["growth"] > 0


def test_score_candidate_stability_focused():
    """Test scoring with stability-focused intent"""
    intent = CorporateIntent(
        growth_weight=0.15,
        profitability_weight=0.25,
        innovation_weight=0.1,
        stability_weight=0.5,
        risk_preference=0.2,
        time_horizon=0.2,
    )
    
    candidate = StrategyCandidate(
        scenario_type=ScenarioType.RECESSION,
        optimization_objective=OptimizationObjective.STABILITY,
        scenario_summary="Defensive strategy",
        objective_vector=ObjectiveVector(growth=80, profitability=14, innovation=0.4, stability=0.9),
        roadmap_title="Stability Focus",
        strategy_count=4,
        key_focus="安定化",
    )
    
    score = score_candidate(intent, candidate)
    
    assert score.score > 0
    assert score.stability_component > score.growth_component


def test_intent_alignment():
    """Test intent alignment calculation"""
    intent = CorporateIntent(
        growth_weight=0.35,
        profitability_weight=0.25,
        innovation_weight=0.25,
        stability_weight=0.15,
    )
    
    candidate = StrategyCandidate(
        scenario_type=ScenarioType.OPTIMISTIC,
        optimization_objective=OptimizationObjective.INNOVATION,
        scenario_summary="Innovation strategy",
        objective_vector=ObjectiveVector(growth=120, profitability=11, innovation=0.85, stability=0.7),
        roadmap_title="Innovation Focus",
        strategy_count=7,
        key_focus="革新",
    )
    
    alignment = calculate_intent_alignment(intent, candidate)
    
    assert alignment.intent_alignment_score >= 0
    assert len(alignment.aligned_objectives) > 0
    assert "innovation" in alignment.aligned_objectives


def test_update_intent_from_history_empty():
    """Test learning from empty history"""
    intent = CorporateIntent()
    history = []
    
    learning = update_intent_from_history(intent, history)
    
    assert learning.cycle_count == 0
    assert learning.learning_confidence == 0.0


def test_apply_learning_to_intent():
    """Test applying learning results to intent"""
    from src.backend.app.models.corporate_intent_model import IntentLearningHistory
    
    original_intent = CorporateIntent(
        growth_weight=0.25,
        profitability_weight=0.25,
        innovation_weight=0.25,
        stability_weight=0.25,
    )
    
    inferred_intent = CorporateIntent(
        growth_weight=0.4,
        profitability_weight=0.2,
        innovation_weight=0.25,
        stability_weight=0.15,
    )
    
    learning = IntentLearningHistory(
        cycle_count=5,
        avg_growth=50.0,
        avg_profitability=10.0,
        avg_innovation=0.5,
        avg_stability=0.6,
        avg_risk_taken=0.5,
        risk_volatility=0.1,
        inferred_intent=inferred_intent,
        learning_confidence=0.5,
    )
    
    updated = apply_learning_to_intent(original_intent, learning)
    
    # Should be blend: 50% original + 50% inferred
    assert 0.25 <= updated.growth_weight <= 0.4
    assert updated.growth_weight > original_intent.growth_weight
