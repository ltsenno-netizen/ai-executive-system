import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from enterprise_evolution_service import EnterpriseEvolutionService


def test_run_and_save_evolution():
    service = EnterpriseEvolutionService()
    period = "2026-01"

    result = service.run_enterprise_evolution(period)

    assert result.period == period
    assert result.evolution_score >= 0

    # Test retrieval
    retrieved = service.get_evolution_result(period)
    assert retrieved is not None
    assert retrieved.period == period
    assert retrieved.evolution_score == result.evolution_score


def test_get_latest_evolution():
    service = EnterpriseEvolutionService()

    latest = service.get_latest_evolution_result()
    if latest:
        assert latest.period
        assert latest.evolution_score >= 0