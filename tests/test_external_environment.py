import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.external_environment_service import ExternalEnvironmentService


def test_load_external_environment():
    service = ExternalEnvironmentService()
    model = service.load_external_environment()

    assert len(model.segments) >= 1
    assert len(model.trends) >= 1
    assert len(model.competitors) >= 1
    assert len(model.shocks) >= 1


def test_calculate_market_size_includes_trend_and_shock():
    service = ExternalEnvironmentService()
    size_july = service.calculate_market_size('stage_market', 7, 2026)
    size_january = service.calculate_market_size('stage_market', 1, 2026)

    assert size_july > 0
    assert size_july != size_january


def test_build_environment_state_structure():
    service = ExternalEnvironmentService()
    state = service.build_environment_state(7, 2026)

    assert state['month'] == 7
    assert state['year'] == 2026
    assert 'market_size_by_segment' in state
    assert 'competitive_pressure_by_segment' in state
    assert isinstance(state['market_size_by_segment'], dict)
    assert isinstance(state['competitive_pressure_by_segment'], dict)


def test_calculate_company_opportunity():
    service = ExternalEnvironmentService()
    state = service.build_environment_state(7, 2026)
    profile = {
        'stage_market': 0.2,
        'digital_distribution_market': 0.2,
        'cm_ad_market': 0.1,
        'md_market': 0.05,
    }
    opportunity = service.calculate_company_opportunity(profile, state)

    assert 'stage_market' in opportunity
    assert opportunity['stage_market'] >= 0
