from src.backend.app.models.executive_simulation_model import ExecutiveSimulationInput, StrategyBundle
from src.backend.app.services.executive_simulation_engine import ExecutiveSimulationEngine
from src.backend.app.services.scenario_simulation_service import ScenarioSimulationService
from src.backend.app.services.strategy_engine_v2_service import StrategyEngineV2Service


def test_run_executive_simulation_produces_report():
    scenario_service = ScenarioSimulationService()
    scenario_service.run_all_simulations()
    scenario_result = scenario_service.get_simulation_result("baseline")
    assert scenario_result is not None

    strategy_report = StrategyEngineV2Service().run_strategy_for_scenario_type("baseline")
    strategy_bundle = StrategyBundle(
        directive_id=strategy_report.report_id,
        scenario_type=strategy_report.scenario_type.value,
        executive_summary=strategy_report.executive_summary,
        directives=strategy_report.strategy_directives,
        recommended_actions=strategy_report.recommended_actions,
        context_notes=strategy_report.scenario_insights[0] if strategy_report.scenario_insights else None,
    )

    engine = ExecutiveSimulationEngine()
    result = engine.run_executive_simulation(
        ExecutiveSimulationInput(scenario_type="baseline", focus_horizon="MID"),
        strategy_bundle,
        scenario_result,
        None,
        None,
    )

    assert result.simulation_id
    assert result.scenario_type == "baseline"
    assert 0.0 <= result.consensus_level <= 1.0
    assert result.strategy_bundle_id == strategy_report.report_id
    assert result.ceo_summary
    assert len(result.comments) == 7
    assert len(result.votes) == 7
