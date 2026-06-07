import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.corporate_fundamentals_service import CorporateFundamentalsService
from app.services.external_environment_service import ExternalEnvironmentService
from app.services.business_portfolio_service import BusinessPortfolioService
from app.services.company_operating_service import CompanyOperatingService


def test_business_units_load_and_distribution():
    service = CorporateFundamentalsService()
    fundamentals = service.load_fundamentals()

    assert len(fundamentals.business_units) == 6
    assert fundamentals.annual_revenue_distribution is not None
    assert abs(fundamentals.annual_revenue_distribution.get('AIタレント', 0.0) - 0.20) < 1e-6
    assert abs(fundamentals.annual_revenue_distribution.get('AIソリューション', 0.0) - 0.10) < 1e-6

    for unit in fundamentals.business_units:
        assert isinstance(unit.revenue_model, list)
        assert isinstance(unit.linked_market_segments, list)
        assert 'gross_margin' in unit.kpis


def test_external_environment_seasonality_and_growth():
    env_service = ExternalEnvironmentService()
    environment = env_service.load_external_environment()

    segment_ids = {segment.id for segment in environment.segments}
    assert 'stage_market' in segment_ids
    assert 'digital_content' in segment_ids
    assert 'digital_ads' in segment_ids
    assert 'ai_solutions' in segment_ids

    stage_size_july = env_service.calculate_market_size('stage_market', 7, 2026)
    assert 50.0 < stage_size_july < 70.0
    ai_solution_size_april = env_service.calculate_market_size('ai_solutions', 4, 2026)
    assert ai_solution_size_april > 60.0


def test_business_portfolio_growth_rate_and_units():
    portfolio_service = BusinessPortfolioService()
    state = portfolio_service.simulate_portfolio_cycle(4)

    assert len(state.portfolio_units) == 6
    assert any(unit.growth_rate > 0.0 for unit in state.portfolio_units)
    assert any(unit.business_unit_id == 'bu_ai_solutions' for unit in state.portfolio_units)
    assert any(unit.business_unit_id == 'bu_live_entertainment' for unit in state.portfolio_units)


def test_company_operating_cost_application():
    operating_service = CompanyOperatingService()
    model = operating_service.prepare_company_model()

    assert model is not None
    assert len(model.monthly_pl) == 12
    assert any(
        any(value > 0 for value in month.revenue.values())
        for month in model.monthly_pl
    )
