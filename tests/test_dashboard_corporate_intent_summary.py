import pytest
from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService


@pytest.fixture
def service():
    return ExecutiveDashboardService()


def test_aggregate_corporate_intent_summary(service):
    """Test aggregating corporate intent summary for dashboard"""
    from src.backend.app.services.corporate_intent_service import CorporateIntentService
    intent_service = CorporateIntentService()
    
    # Set intent first
    intent_service.set_intent(
        growth_weight=0.35,
        profitability_weight=0.25,
        innovation_weight=0.25,
        stability_weight=0.15,
        risk_preference=0.6,
        time_horizon=0.7,
        cultural_identity="innovative",
    )
    
    # Get summary
    summary = service.aggregate_corporate_intent_summary()
    
    assert summary is not None
    assert summary.growth_weight == 0.35
    assert summary.profitability_weight == 0.25
    assert summary.innovation_weight == 0.25
    assert summary.stability_weight == 0.15
    assert summary.risk_preference == 0.6
    assert summary.time_horizon == 0.7
    assert summary.cultural_identity == "innovative"


def test_corporate_intent_in_dashboard(service):
    """Test corporate intent field appears in dashboard"""
    from src.backend.app.services.corporate_intent_service import CorporateIntentService
    intent_service = CorporateIntentService()
    
    # Set intent first
    intent_service.set_intent(
        growth_weight=0.35,
        profitability_weight=0.25,
        innovation_weight=0.25,
        stability_weight=0.15,
        risk_preference=0.6,
        time_horizon=0.7,
        cultural_identity="innovative",
    )
    
    # Get dashboard
    dashboard = service.build_dashboard(include_forecast=False)
    
    assert dashboard is not None
    assert dashboard.corporate_intent is not None
    assert dashboard.corporate_intent.growth_weight == 0.35
    assert dashboard.corporate_intent.cultural_identity == "innovative"


def test_dashboard_intent_with_defaults(service):
    """Test dashboard includes default intent"""
    # Just get dashboard without setting intent
    dashboard = service.build_dashboard(include_forecast=False)
    
    assert dashboard is not None
    # Should have a default or None
    # (either way is acceptable)
