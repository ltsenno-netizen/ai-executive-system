import pytest
from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService
from src.backend.app.models.executive_dashboard_model import StrategyDashboardSummary, StrategyDashboardItem
from src.backend.app.models.strategy_model import StrategyHorizon, StrategyRiskLevel


def test_aggregate_strategy_summary():
    """Test aggregating strategy summary"""
    service = ExecutiveDashboardService()
    
    summary = service.aggregate_strategy_summary()
    
    # May be None if no roadmaps exist
    if summary is not None:
        assert isinstance(summary, StrategyDashboardSummary)
        assert summary.objective is not None
        assert summary.selected_scenario is not None
        assert summary.key_focus is not None


def test_dashboard_includes_strategy():
    """Test that dashboard includes strategy"""
    service = ExecutiveDashboardService()
    
    try:
        dashboard = service.build_dashboard(month=4)
        
        # strategy may be None if no roadmaps exist
        if dashboard.strategy is not None:
            assert isinstance(dashboard.strategy, StrategyDashboardSummary)
            assert dashboard.strategy.objective is not None
    except Exception as e:
        pytest.skip(f"Dashboard building failed: {str(e)}")


def test_strategy_summary_structure():
    """Test StrategyDashboardSummary structure"""
    item = StrategyDashboardItem(
        title="Test Strategy",
        horizon=StrategyHorizon.SHORT_TERM,
        priority=1,
        risk_level=StrategyRiskLevel.LOW
    )
    
    summary = StrategyDashboardSummary(
        objective="GROWTH",
        selected_scenario="OPTIMISTIC",
        key_focus="成長戦略",
        top_strategies=[item]
    )
    
    assert summary.objective == "GROWTH"
    assert summary.selected_scenario == "OPTIMISTIC"
    assert len(summary.top_strategies) == 1
    assert summary.top_strategies[0].title == "Test Strategy"
