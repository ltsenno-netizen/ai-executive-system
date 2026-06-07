import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.services.business_portfolio_service import BusinessPortfolioService
from app.services.corporate_fundamentals_service import CorporateFundamentalsService

client = TestClient(app)


def test_build_portfolio_units_basic():
    service = BusinessPortfolioService()
    fundamentals = CorporateFundamentalsService().load_fundamentals()
    environment_state = service.environment_service.build_environment_state(7, 2026)
    pl_data = service.integration_service.simulate_month_full(7)['pl']

    units = service.build_portfolio_units(7, fundamentals, environment_state, pl_data)

    assert len(units) >= 1
    assert all(unit.revenue >= 0 for unit in units)
    assert all(0.0 <= unit.strategic_fit <= 1.0 for unit in units)
    assert all(0.0 <= unit.risk_score <= 1.0 for unit in units)


def test_generate_investment_decisions_by_style():
    service = BusinessPortfolioService()
    fundamentals = CorporateFundamentalsService().load_fundamentals()
    environment_state = service.environment_service.build_environment_state(7, 2026)
    pl_data = service.integration_service.simulate_month_full(7)['pl']

    units = service.build_portfolio_units(7, fundamentals, environment_state, pl_data)
    decisions = service.generate_portfolio_decisions(units, fundamentals)

    assert len(decisions) >= 1
    assert any(decision.decision in {'Invest', 'Maintain', 'Reduce', 'Exit', 'NewBusiness'} for decision in decisions)
    assert all(decision.required_budget >= 0 for decision in decisions)


def test_simulate_portfolio_cycle_returns_state():
    service = BusinessPortfolioService()
    state = service.simulate_portfolio_cycle(7)

    assert state.month == 7
    assert len(state.portfolio_units) >= 1
    assert len(state.decisions) >= 1
    assert state.decisions[0].business_unit_id != ''


def test_get_portfolio_api():
    response = client.get('/api/portfolio?month=7')
    assert response.status_code == 200
    body = response.json()
    assert body['month'] == 7
    assert 'portfolio_units' in body
    assert 'decisions' in body


def test_get_portfolio_decisions_api():
    response = client.get('/api/portfolio/decisions?month=7')
    assert response.status_code == 200
    decisions = response.json()
    assert isinstance(decisions, list)
    assert decisions[0]['decision'] in {'Invest', 'Maintain', 'Reduce', 'Exit', 'NewBusiness'}


def test_get_portfolio_units_api():
    response = client.get('/api/portfolio/units?month=7')
    assert response.status_code == 200
    units = response.json()
    assert isinstance(units, list)
    assert 'business_unit_id' in units[0]
    assert 'investment_need' in units[0]
