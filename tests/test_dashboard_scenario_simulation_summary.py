from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService
from src.backend.app.services.scenario_simulation_service import ScenarioSimulationService


def test_dashboard_aggregates_scenario_simulation_preview():
    simulation_service = ScenarioSimulationService()
    simulation_service.run_all_simulations()

    dashboard_service = ExecutiveDashboardService()
    summary = dashboard_service.aggregate_market_summary(month=1)

    assert summary.scenario_simulation_summary is not None
    assert summary.scenario_simulation_summary.scenario_type in [
        "baseline",
        "optimistic",
        "pessimistic",
        "tech_boom",
        "recession",
    ]
    assert isinstance(summary.scenario_simulation_summary.confidence, float)
    assert isinstance(summary.scenario_simulation_summary.key_impacts, dict)
    assert isinstance(summary.scenario_simulation_summary.contingency_recommendations, list)
