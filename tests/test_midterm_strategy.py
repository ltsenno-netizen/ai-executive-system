import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'backend'))

from app.services.midterm_strategy_service import MidtermStrategyService
from app.services.company_operations_integration_service import CompanyOperationsIntegrationService


def test_gap_analysis_and_recommendation():
    service = MidtermStrategyService()
    model = service.load_strategy_model()
    current_kpis = {
        'license_ratio': 0.12,
        'digital_ratio': 0.10,
        'performance_profit_margin': 0.12,
        'ip_revenue': 5.0,
        'overseas_revenue': 1.0,
    }

    gaps = service.evaluate_kpi_gap(current_kpis, model)
    assert any(gap.kpi_name == 'license_ratio' for gap in gaps)
    assert any(gap.severity == 'High' for gap in gaps)

    recommendations = service.recommend_initiatives(gaps, model)
    assert len(recommendations) >= 1
    assert recommendations[0].theme_id is not None


def test_simulate_year_with_strategy():
    integration = CompanyOperationsIntegrationService()
    service = MidtermStrategyService()

    result = service.simulate_year_with_strategy(2026)
    assert result['year'] == 2026
    assert 'annual_kpis' in result
    assert 'gaps' in result
    assert 'recommendations' in result
    assert len(result['monthly_results']) == 12

    # PL側と operations側が含まれることを確認
    sample_month = result['monthly_results'][0]
    assert 'pl' in sample_month
    assert 'operations' in sample_month


if __name__ == '__main__':
    test_gap_analysis_and_recommendation()
    test_simulate_year_with_strategy()
    print('test_midterm_strategy passed')
