import os
import sys

from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.main import app
from app.services.corporate_fundamentals_service import CorporateFundamentalsService

client = TestClient(app)


def test_load_corporate_fundamentals():
    service = CorporateFundamentalsService()
    model = service.load_fundamentals()

    assert model.profile.name != ''
    assert len(model.business_units) >= 1
    assert len(model.customer_segments) >= 1
    assert model.financials.cash_reserves >= 0


def test_build_monthly_fundamentals_impact():
    service = CorporateFundamentalsService()
    result = service.build_monthly_fundamentals_impact(7, 2026)

    assert result['month'] == 7
    assert 'fundamentals' in result
    assert 'baseline_pl' in result
    assert 'adjusted_pl' in result
    assert 'adjusted_kpis' in result
    assert result['fundamentals']['profile']['name'] != ''


def test_get_corporate_fundamentals_endpoint():
    response = client.get('/api/fundamentals')
    assert response.status_code == 200
    body = response.json()
    assert 'profile' in body
    assert 'business_units' in body


def test_get_fundamentals_impact_endpoint():
    response = client.get('/api/fundamentals/impact?month=7&year=2026')
    assert response.status_code == 200
    body = response.json()
    assert body['month'] == 7
    assert 'adjusted_pl' in body
    assert 'adjusted_kpis' in body
