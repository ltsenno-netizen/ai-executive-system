import os
from src.backend.app.services.scenario_simulation_service import ScenarioSimulationService
from src.backend.app.models.scenario_model import ScenarioType


def test_run_all_scenario_simulations_and_save_files():
    service = ScenarioSimulationService()
    results = service.run_all_simulations()

    assert len(results) == 5
    for result in results:
        assert result.scenario_type in [ScenarioType.BASELINE, ScenarioType.OPTIMISTIC, ScenarioType.PESSIMISTIC, ScenarioType.TECH_BOOM, ScenarioType.RECESSION]
        file_path = os.path.join(service.storage_dir, f"{result.scenario_type.value}.json")
        assert os.path.exists(file_path)


def test_get_specific_scenario_simulation_result():
    service = ScenarioSimulationService()
    service.run_all_simulations()

    for scenario_type in ScenarioType:
        result = service.get_simulation_result(scenario_type.value)
        assert result is not None
        assert result.scenario_type == scenario_type
        assert result.projected_environment is not None
        assert result.projected_culture is not None
        assert isinstance(result.financial_impact_summary, dict)
        assert "revenue" in result.financial_impact_summary


def test_get_all_scenario_simulation_results_returns_sorted_list():
    service = ScenarioSimulationService()
    service.run_all_simulations()
    results = service.get_all_simulation_results()

    assert isinstance(results, list)
    assert len(results) >= 5
    assert all(hasattr(r, "created_at") for r in results)
