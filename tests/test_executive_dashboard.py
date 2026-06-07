import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.executive_dashboard_service import ExecutiveDashboardService


def test_build_dashboard_contains_all_sections():
    service = ExecutiveDashboardService()
    dashboard = service.build_dashboard(7)

    assert dashboard.month == 7
    assert dashboard.pl.revenue >= 0
    assert dashboard.kpis.month == 7
    assert dashboard.operations.month == 7
    assert dashboard.issues.month == 7
    assert dashboard.improvements.month == 7
    assert isinstance(dashboard.improvements.updated_priorities, dict)


def test_forecast_next_month_returns_summary():
    service = ExecutiveDashboardService()
    forecast = service.forecast_next_month(7)

    assert forecast['month'] == 7
    assert 'pl' in forecast
    assert 'operations' in forecast
    assert 'actions_executed' in forecast
    assert 'updated_priorities' in forecast


def test_dashboard_aggregates_consistent_metrics():
    service = ExecutiveDashboardService()
    dashboard = service.build_dashboard(5)

    assert dashboard.pl.month == dashboard.kpis.month == dashboard.operations.month == dashboard.issues.month == dashboard.improvements.month
    assert isinstance(dashboard.pl.profit_margin, float)
    assert isinstance(dashboard.operations.active_tasks, int)
    assert isinstance(dashboard.operations.incidents, int)
    assert dashboard.customer_summary is not None
    assert len(dashboard.customer_summary.segments) >= 1
    assert all(segment.estimated_customers >= 0 for segment in dashboard.customer_summary.segments)
