import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'backend'))

from app.services.company_operating_service import CompanyOperatingService
from app.services.annual_operations_service import AnnualOperationsService
from app.services.company_operations_integration_service import CompanyOperationsIntegrationService


def test_simulate_month_full_consistency():
    integration = CompanyOperationsIntegrationService()
    company_service = CompanyOperatingService()
    operations_service = AnnualOperationsService()

    result = integration.simulate_month_full(7)
    assert result['month'] == 7

    environment_state = integration.environment_service.build_environment_state(7, 2026)
    expected_pl = company_service.simulate_month(7, environment_state=environment_state).model_dump()
    assert result['pl'] == expected_pl

    expected_operations = operations_service.simulate_month_operations(7)
    assert result['operations'] == expected_operations


def test_simulate_month_full_all_months():
    integration = CompanyOperationsIntegrationService()
    for month in range(1, 13):
        result = integration.simulate_month_full(month)
        assert result['month'] == month
        assert 'pl' in result
        assert 'operations' in result
        assert result['pl']['month'] == month
        assert result['operations']['month'] == month


if __name__ == '__main__':
    test_simulate_month_full_consistency()
    test_simulate_month_full_all_months()
    print('test_company_operations_integration passed')
