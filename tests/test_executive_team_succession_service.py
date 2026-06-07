import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from src.backend.executive_team_succession_service import ExecutiveTeamSuccessionService
from src.backend.executive_team_succession_model import ExecutiveRole


def test_run_executive_succession():
    service = ExecutiveTeamSuccessionService()
    # Placeholder environment and culture
    environment = None
    culture = None

    decisions = service.run_executive_succession("2026-01", environment, culture)

    assert len(decisions) == 4  # CFO, COO, CMO, CHRO
    roles = {d.role for d in decisions}
    assert roles == {ExecutiveRole.CFO, ExecutiveRole.COO, ExecutiveRole.CMO, ExecutiveRole.CHRO}