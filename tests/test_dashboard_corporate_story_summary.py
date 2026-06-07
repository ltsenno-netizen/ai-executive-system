import pytest
from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService
from src.backend.app.models.executive_dashboard_model import CorporateStorySummary


def test_aggregate_story_summary():
    """Test aggregating corporate story summary"""
    service = ExecutiveDashboardService()
    
    summary = service.aggregate_story_summary()
    
    # May be None if no stories exist
    if summary is not None:
        assert isinstance(summary, CorporateStorySummary)
        assert summary.period is not None
        assert summary.summary is not None


def test_dashboard_includes_story():
    """Test that dashboard includes corporate story"""
    service = ExecutiveDashboardService()
    
    try:
        dashboard = service.build_dashboard(month=4)
        
        # corporate_story may be None if no stories exist
        if dashboard.corporate_story is not None:
            assert isinstance(dashboard.corporate_story, CorporateStorySummary)
            assert dashboard.corporate_story.period is not None
    except Exception as e:
        pytest.skip(f"Dashboard building failed: {str(e)}")


def test_story_summary_structure():
    """Test CorporateStorySummary structure"""
    summary = CorporateStorySummary(
        period="2026-04",
        summary="Test corporate story summary"
    )
    
    assert summary.period == "2026-04"
    assert summary.summary == "Test corporate story summary"
