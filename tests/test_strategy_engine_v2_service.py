import os

from src.backend.app.services.strategy_engine_v2_service import StrategyEngineV2Service


def test_strategy_engine_v2_service_runs_and_persists_report(tmp_path):
    service = StrategyEngineV2Service()
    service.storage_dir = str(tmp_path)
    os.makedirs(service.storage_dir, exist_ok=True)

    report = service.run_strategy_for_scenario_type("baseline")

    assert report is not None
    assert report.scenario_type.value == "baseline"
    assert report.executive_summary

    loaded_report = service.get_report("baseline")
    assert loaded_report is not None
    assert loaded_report.report_id == report.report_id

    markdown = service.export_report_markdown("baseline")
    assert markdown is not None
    assert "Executive Summary" in markdown
