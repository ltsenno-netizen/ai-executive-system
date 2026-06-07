from src.backend.app.models.executive_simulation_model import ExecutiveSimulationInput
from src.backend.app.services.executive_simulation_service import ExecutiveSimulationService


def test_run_simulation_persists_history():
    service = ExecutiveSimulationService()
    input_data = ExecutiveSimulationInput(scenario_type="baseline", focus_horizon="MID")
    result = service.run_simulation(input_data)

    assert result.simulation_id
    assert result.timestamp is not None
    assert 0.0 <= result.consensus_level <= 1.0
    latest = service.get_latest()
    assert latest is not None
    assert latest.simulation_id == result.simulation_id
    assert service.get_by_id(result.simulation_id) is not None
    assert len(service.list_recent(1)) >= 1
