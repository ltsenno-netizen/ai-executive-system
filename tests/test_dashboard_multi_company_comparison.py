"""
Dashboard Multi-Company Comparative Integration Tests (Step AK)
"""

from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService
from src.backend.app.models.multi_company_comparative_model import CompanyId
from src.backend.app.services.multi_company_comparative_service import MultiCompanyComparativeService


def test_dashboard_includes_multi_company_comparison():
    """Test that dashboard includes multi-company comparison summary."""
    # Generate comparison
    multi_service = MultiCompanyComparativeService()
    company_ids = [
        CompanyId(company_id="self", name="Our Company"),
        CompanyId(company_id="comp_a", name="Competitor A"),
        CompanyId(company_id="comp_b", name="Competitor B"),
    ]
    multi_service.compare_companies(company_ids)
    
    # Build dashboard
    dashboard_service = ExecutiveDashboardService()
    dashboard = dashboard_service.build_dashboard(1)
    
    # Verify multi-company comparison summary is included
    assert dashboard.multi_company_comparison_summary is not None
    assert dashboard.multi_company_comparison_summary.companies is not None
    assert len(dashboard.multi_company_comparison_summary.companies) > 0
    assert dashboard.multi_company_comparison_summary.cluster_count >= 0
    assert dashboard.multi_company_comparison_summary.key_insight is not None


def test_dashboard_handles_missing_comparison():
    """Test dashboard gracefully handles no comparison available."""
    dashboard_service = ExecutiveDashboardService()
    dashboard = dashboard_service.build_dashboard(1)
    
    # Should still build dashboard even without comparison
    assert dashboard.month == 1
    assert dashboard.pl is not None
    # multi_company_comparison_summary may be None if no comparison available


def test_multi_company_summary_format():
    """Test multi-company summary has correct format."""
    multi_service = MultiCompanyComparativeService()
    company_ids = [
        CompanyId(company_id="a", name="Company A"),
        CompanyId(company_id="b", name="Company B"),
    ]
    report = multi_service.compare_companies(company_ids)
    
    # Should have proper structure
    assert hasattr(report, 'metrics')
    assert hasattr(report, 'clusters')
    assert hasattr(report, 'dimensions')
    assert hasattr(report, 'narrative_summary')
    
    # Metrics should be organized
    assert len(report.metrics) > 0
    for metric in report.metrics:
        assert metric.category is not None
        assert metric.values is not None
