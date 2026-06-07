from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService


def test_dashboard_autopilot_summary_does_not_fail():
    dashboard_service = ExecutiveDashboardService()
    summary = dashboard_service._aggregate_enterprise_autopilot_summary()

    assert summary is None or summary.last_cycle_id is not None
    assert summary is None or summary.average_phase_success_rate >= 0.0
