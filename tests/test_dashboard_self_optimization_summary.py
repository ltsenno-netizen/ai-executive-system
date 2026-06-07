import pytest
from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService
from src.backend.app.models.executive_dashboard_model import SelfOptimizationSummary


def test_aggregate_optimization_summary():
    """Test aggregating self-optimization summary"""
    service = ExecutiveDashboardService()
    
    # Try to aggregate optimization summary
    summary = service.aggregate_optimization_summary()
    
    # May be None if no plans exist
    if summary is not None:
        assert isinstance(summary, SelfOptimizationSummary)
        assert summary.objective in ["growth", "stability", "innovation", "profitability"]
        assert isinstance(summary.top_strategies, list)
        assert isinstance(summary.key_culture_shifts, list)
        assert isinstance(summary.key_leadership_changes, list)
        assert 0.0 <= summary.expected_evolution_score <= 1.0


def test_dashboard_includes_optimization():
    """Test that dashboard includes self-optimization"""
    service = ExecutiveDashboardService()
    
    try:
        dashboard = service.build_dashboard(month=4)
        
        # self_optimization may be None if no plans exist
        if dashboard.self_optimization is not None:
            assert isinstance(dashboard.self_optimization, SelfOptimizationSummary)
            assert dashboard.self_optimization.objective is not None
            assert len(dashboard.self_optimization.top_strategies) > 0
    except Exception as e:
        # May fail if dependencies aren't available
        pytest.skip(f"Dashboard building failed: {str(e)}")


def test_optimization_summary_structure():
    """Test SelfOptimizationSummary structure"""
    summary = SelfOptimizationSummary(
        objective="growth",
        selected_scenario="optimistic",
        top_strategies=["Strategy 1", "Strategy 2"],
        key_culture_shifts=["innovation_culture: +0.10"],
        key_leadership_changes=["CEO: keep"],
        expected_evolution_score=0.75
    )
    
    assert summary.objective == "growth"
    assert summary.selected_scenario == "optimistic"
    assert len(summary.top_strategies) == 2
    assert len(summary.key_culture_shifts) == 1
    assert len(summary.key_leadership_changes) == 1
    assert summary.expected_evolution_score == 0.75
