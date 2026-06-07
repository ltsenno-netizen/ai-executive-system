import os
import sys
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.company_operating_service import CompanyOperatingService
from app.services.corporate_fundamentals_service import CorporateFundamentalsService
from app.services.external_environment_service import ExternalEnvironmentService


def test_customer_segments_structure():
    fundamentals = CorporateFundamentalsService().load_fundamentals()

    assert len(fundamentals.customer_segments) == 5
    for segment in fundamentals.customer_segments:
        assert segment.id != ''
        assert segment.name in {'Core Fans', 'Light Fans', 'Advertisers', 'Digital Platforms', 'Enterprise Clients'}
        assert 'purchase_frequency' in segment.behavior_patterns
        assert 'avg_spend' in segment.behavior_patterns
        assert 'digital_engagement' in segment.behavior_patterns
        assert 'price' in segment.sensitivity
        assert 'trend' in segment.sensitivity
        assert 'promotion' in segment.sensitivity
        assert isinstance(segment.linked_business_units, list)
        assert len(segment.linked_business_units) >= 1


def test_apply_customers_to_revenue_changes_monthly_revenue():
    company_service = CompanyOperatingService()
    fundamentals = CorporateFundamentalsService().load_fundamentals()
    environment_state = ExternalEnvironmentService().build_environment_state(7, 2026)

    base_model = company_service.prepare_company_model()
    baseline_month = next((item for item in base_model.monthly_pl if item.month == 7), None)
    assert baseline_month is not None

    modified_month = deepcopy(baseline_month)
    company_service.apply_customers_to_revenue(modified_month, fundamentals, environment_state)

    baseline_total = sum(baseline_month.revenue.values())
    modified_total = sum(modified_month.revenue.values())
    assert modified_total != baseline_total
    assert modified_total > 0


def test_customer_segments_summary_in_dashboard():
    from app.services.executive_dashboard_service import ExecutiveDashboardService

    dashboard_service = ExecutiveDashboardService()
    dashboard = dashboard_service.build_dashboard(7)

    assert dashboard.customer_summary is not None
    assert len(dashboard.customer_summary.segments) == 5
    core_fans = next((s for s in dashboard.customer_summary.segments if s.name == 'Core Fans'), None)
    assert core_fans is not None
    assert core_fans.purchase_frequency == 1.5
    assert core_fans.avg_spend == 1.2
    assert 'bu_live_entertainment' in core_fans.linked_business_units
