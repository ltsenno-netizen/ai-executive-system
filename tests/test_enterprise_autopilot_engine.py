import pytest

from src.backend.app.services.enterprise_autopilot_engine import EnterpriseAutopilotEngine


def test_run_autopilot_cycle_completes():
    engine = EnterpriseAutopilotEngine()
    cycle = engine.run_autopilot_cycle("test-cycle")

    assert cycle.cycle_id == "test-cycle"
    assert cycle.completed_at is not None
    assert cycle.summary is not None
    assert cycle.overall_status in {"COMPLETED", "FAILED"}
    assert len(cycle.phases) >= 1


def test_perception_phase_has_summary():
    engine = EnterpriseAutopilotEngine()
    phase = engine.run_perception()

    assert phase.phase.name == "PERCEPTION"
    assert "Observing" in phase.summary
