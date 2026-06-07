import pytest
from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService


@pytest.fixture
def service():
    return ExecutiveDashboardService()


def test_aggregate_multi_objective_summary(service):
    """Test aggregating multi-objective summary for dashboard"""
    # First generate data
    from src.backend.app.services.multi_objective_service import MultiObjectiveService
    multi_service = MultiObjectiveService()
    multi_service.generate_multi_objective_analysis()
    
    # Get summary
    summary = service.aggregate_multi_objective_summary()
    
    assert summary is not None
    assert summary.frontier_count > 0
    assert summary.best_growth >= 0
    assert summary.best_profitability >= 0
    assert 0 <= summary.best_innovation <= 1
    assert 0 <= summary.best_stability <= 1
    assert summary.pareto_candidates > 0


def test_multi_objective_in_dashboard(service):
    """Test multi-objective field appears in dashboard"""
    from src.backend.app.services.multi_objective_service import MultiObjectiveService
    multi_service = MultiObjectiveService()
    multi_service.generate_multi_objective_analysis()
    
    # Get dashboard for current month
    dashboard = service.build_dashboard(include_forecast=False)
    
    assert dashboard is not None
    assert dashboard.multi_objective is not None
    assert dashboard.multi_objective.frontier_count > 0
