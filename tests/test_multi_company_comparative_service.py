"""
Multi-Company Comparative Service Tests (Step AK)
"""

from src.backend.app.models.multi_company_comparative_model import CompanyId
from src.backend.app.services.multi_company_comparative_service import MultiCompanyComparativeService


def test_compare_companies():
    """Test end-to-end comparison."""
    service = MultiCompanyComparativeService()
    
    company_ids = [
        CompanyId(company_id="self", name="Our Company"),
        CompanyId(company_id="competitor_a", name="Competitor A"),
        CompanyId(company_id="competitor_b", name="Competitor B"),
    ]
    
    report = service.compare_companies(company_ids)
    
    assert report.report_id is not None
    assert len(report.companies) == 3
    assert len(report.metrics) > 0
    assert len(report.clusters) > 0


def test_get_last_comparison():
    """Test retrieval of last comparison."""
    service = MultiCompanyComparativeService()
    
    company_ids = [
        CompanyId(company_id="a", name="A"),
        CompanyId(company_id="b", name="B"),
    ]
    
    report1 = service.compare_companies(company_ids)
    report_retrieved = service.get_last_comparison()
    
    assert report_retrieved is not None
    assert report_retrieved.report_id == report1.report_id


def test_get_report_by_id():
    """Test retrieval of specific report."""
    service = MultiCompanyComparativeService()
    
    company_ids = [
        CompanyId(company_id="a", name="A"),
        CompanyId(company_id="b", name="B"),
    ]
    
    report = service.compare_companies(company_ids)
    retrieved = service.get_report_by_id(report.report_id)
    
    assert retrieved is not None
    assert retrieved.report_id == report.report_id


def test_list_available_companies():
    """Test listing available companies."""
    service = MultiCompanyComparativeService()
    companies = service.list_available_companies()
    
    assert len(companies) > 0
    assert all(hasattr(c, 'company_id') for c in companies)
    assert all(hasattr(c, 'name') for c in companies)


def test_generate_markdown_report():
    """Test markdown report generation."""
    service = MultiCompanyComparativeService()
    
    company_ids = [
        CompanyId(company_id="a", name="A"),
        CompanyId(company_id="b", name="B"),
    ]
    
    report = service.compare_companies(company_ids)
    markdown = service.generate_markdown_report(report)
    
    assert "Multi-Company Comparative Intelligence Report" in markdown
    assert "## Executive Summary" in markdown
    assert "## Comparative Metrics" in markdown
    assert "## Company Archetypes" in markdown
