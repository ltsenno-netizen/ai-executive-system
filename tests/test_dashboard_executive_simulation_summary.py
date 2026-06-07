from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService
from src.backend.app.services.executive_simulation_service import ExecutiveSimulationService
from src.backend.app.models.executive_simulation_model import ExecutiveSimulationInput


def test_dashboard_includes_executive_simulation_summary():
    simulation_service = ExecutiveSimulationService()
    simulation_service.run_simulation(ExecutiveSimulationInput(scenario_type="baseline", focus_horizon="MID"))

    dashboard_service = ExecutiveDashboardService()
    summary = dashboard_service._aggregate_executive_simulation_summary()

    assert summary is not None
    assert summary.last_simulation_id
    assert 0.0 <= summary.consensus_level <= 1.0
    assert isinstance(summary.approved, bool)
