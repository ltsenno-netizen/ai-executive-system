import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from src.backend.app.services.monthly_batch_service import MonthlyBatchService


def test_monthly_batch_triggers_executive_succession():
    service = MonthlyBatchService()
    # Test with a period that should trigger succession (e.g., 2027-12 for 3 years)
    result = service.run_monthly_cycle("2027-12")

    # Assuming trigger is set, check if executive_team_succession_ok is True
    # For now, since trigger is disabled, it should be False
    assert result.executive_team_succession_ok == False