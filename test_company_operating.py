import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'backend'))

from app.services.company_operating_service import CompanyOperatingService


def test_company_operating_service():
    service = CompanyOperatingService()
    model = service.prepare_company_model()

    assert len(model.monthly_pl) == 12
    assert len(model.kpis) == 12

    july = service.simulate_month(7)
    assert july.month == 7
    assert july.profit is not None
    assert july.cash_balance is not None
    assert 'license_ratio' in july.kpis
    assert july.kpis['license_ratio'] >= 0.0

    month_one = next((m for m in model.monthly_pl if m.month == 1), None)
    assert month_one is not None
    assert isinstance(month_one.profit_margin, float)
    assert isinstance(month_one.cash_flow, float)


if __name__ == '__main__':
    test_company_operating_service()
    print('company operating service test passed')
