import os
import sys
import tempfile
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.company_operations_integration_service import CompanyOperationsIntegrationService
from app.services.improvement_cycle_service import ImprovementCycleService
from app.services.executive_dashboard_service import ExecutiveDashboardService


def test_simulate_month_full_annual_loop():
    service = CompanyOperationsIntegrationService()
    for month in range(1, 13):
        result = service.simulate_month_full(month)
        assert result['month'] == month
        assert 'pl' in result
        assert 'operations' in result


def test_simulate_cycle_three_months():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_state = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'samples', 'improvement_cycle_state.json'))
        dest_state = os.path.join(temp_dir, 'improvement_cycle_state.json')
        shutil.copyfile(source_state, dest_state)

        service = ImprovementCycleService(data_path=temp_dir)
        for month in [1, 2, 3]:
            result = service.simulate_month_cycle(month)
            assert result['month'] == month
            assert 'issues' in result
            assert 'actions_executed' in result
            assert 'updated_priorities' in result


def test_dashboard_api_returns_full_summary():
    service = ExecutiveDashboardService()
    dashboard = service.build_dashboard(7)

    assert dashboard.month == 7
    assert dashboard.pl.revenue >= 0
    assert dashboard.kpis.month == 7
    assert dashboard.operations.active_tasks >= 0
    assert isinstance(dashboard.issues.issues, list)
    assert isinstance(dashboard.improvements.updated_priorities, dict)


def test_strategy_issues_improvement_dashboard_flow():
    service = CompanyOperationsIntegrationService()
    monthly_state = service.simulate_month_full(7)
    assert 'pl' in monthly_state
    assert 'operations' in monthly_state

    dashboard_service = ExecutiveDashboardService()
    dashboard = dashboard_service.build_dashboard(7)
    assert dashboard.issues.month == 7
    assert dashboard.improvements.month == 7
    assert dashboard.pl.month == 7
