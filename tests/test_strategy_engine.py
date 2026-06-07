import pytest
from src.backend.app.services.strategy_engine import (
    determine_key_focus,
    build_strategy_items,
    build_strategy_roadmap,
)
from src.backend.app.models.self_optimization_model import OptimizationObjective, SelfOptimizationPlan, StrategyAdjustment, CultureAdjustment, LeadershipAdjustment
from src.backend.app.models.scenario_model import ScenarioType
from src.backend.app.models.corporate_story_model import CorporateStory, CorporateStorySection


def test_determine_key_focus_growth():
    """Test focus determination for GROWTH objective"""
    plan = SelfOptimizationPlan(
        objective=OptimizationObjective.GROWTH,
        selected_scenario=ScenarioType.OPTIMISTIC,
        recommended_strategies=[],
        recommended_culture_shifts=[],
        recommended_leadership_changes=[],
        expected_evolution_score=0.75
    )
    
    focus = determine_key_focus(plan)
    
    assert "成長" in focus
    assert "新規市場" in focus


def test_determine_key_focus_stability():
    """Test focus determination for STABILITY objective"""
    plan = SelfOptimizationPlan(
        objective=OptimizationObjective.STABILITY,
        selected_scenario=ScenarioType.BASELINE,
        recommended_strategies=[],
        recommended_culture_shifts=[],
        recommended_leadership_changes=[],
        expected_evolution_score=0.65
    )
    
    focus = determine_key_focus(plan)
    
    assert "安定" in focus
    assert "キャッシュフロー" in focus


def test_build_strategy_items():
    """Test strategy item generation"""
    plan = SelfOptimizationPlan(
        objective=OptimizationObjective.GROWTH,
        selected_scenario=ScenarioType.OPTIMISTIC,
        recommended_strategies=[
            StrategyAdjustment(
                strategy_name="新規事業投資",
                description="テック企業との協業",
                priority=1,
                expected_impact=0.8
            )
        ],
        recommended_culture_shifts=[
            CultureAdjustment(
                culture_type="innovation_culture",
                shift_direction="enhance",
                target_level=0.8
            )
        ],
        recommended_leadership_changes=[],
        expected_evolution_score=0.75
    )
    
    story = CorporateStory(
        period="2026-04",
        sections=[],
        summary="Test story"
    )
    
    items = build_strategy_items(plan, story)
    
    assert len(items) >= 2  # At least strategy and culture shift
    assert any("新規事業" in item.title for item in items)
    assert any("文化" in item.title for item in items)


def test_build_strategy_roadmap():
    """Test complete roadmap generation"""
    plan = SelfOptimizationPlan(
        objective=OptimizationObjective.GROWTH,
        selected_scenario=ScenarioType.OPTIMISTIC,
        recommended_strategies=[
            StrategyAdjustment(
                strategy_name="新規事業投資",
                description="テック企業との協業",
                priority=1,
                expected_impact=0.8
            )
        ],
        recommended_culture_shifts=[],
        recommended_leadership_changes=[],
        expected_evolution_score=0.75
    )
    
    story = CorporateStory(
        period="2026-04",
        sections=[
            CorporateStorySection(title="Test", content="Test content")
        ],
        summary="Test story"
    )
    
    roadmap = build_strategy_roadmap(plan, story)
    
    assert roadmap.objective == OptimizationObjective.GROWTH
    assert roadmap.selected_scenario == ScenarioType.OPTIMISTIC
    assert len(roadmap.strategies) > 0
    assert roadmap.key_focus is not None
    assert "成長" in roadmap.key_focus
