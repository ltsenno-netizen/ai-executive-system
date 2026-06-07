from src.backend.app.services.enterprise_autopilot_service import EnterpriseAutopilotService


def test_run_cycle_persists_result():
    service = EnterpriseAutopilotService()
    cycle = service.run_cycle()

    assert cycle.cycle_id is not None
    assert cycle.completed_at is not None
    assert cycle.overall_status in {"COMPLETED", "FAILED"}
    latest = service.get_latest_cycle()
    assert latest is not None
    assert latest.cycle_id == cycle.cycle_id
