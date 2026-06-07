import pytest
from src.backend.app.services.corporate_intent_service import CorporateIntentService
from src.backend.app.models.corporate_intent_model import CorporateIntent


@pytest.fixture
def service():
    return CorporateIntentService()


def test_get_intent(service):
    """Test getting current intent"""
    intent = service.get_intent()
    
    assert intent is not None
    assert isinstance(intent, CorporateIntent)
    assert 0 <= intent.growth_weight <= 1
    assert 0 <= intent.profitability_weight <= 1
    assert 0 <= intent.innovation_weight <= 1
    assert 0 <= intent.stability_weight <= 1


def test_set_intent(service):
    """Test setting intent"""
    new_intent = service.set_intent(
        growth_weight=0.4,
        profitability_weight=0.2,
        innovation_weight=0.25,
        stability_weight=0.15,
        risk_preference=0.6,
        time_horizon=0.7,
        cultural_identity="innovative",
    )
    
    assert new_intent.growth_weight == 0.4
    assert new_intent.profitability_weight == 0.2
    assert new_intent.risk_preference == 0.6
    assert new_intent.cultural_identity == "innovative"
    
    # Verify it was saved
    retrieved = service.get_intent()
    assert retrieved.growth_weight == new_intent.growth_weight


def test_intent_normalization(service):
    """Test that weights are normalized"""
    new_intent = service.set_intent(
        growth_weight=0.5,
        profitability_weight=0.3,
        innovation_weight=0.3,
        stability_weight=0.2,
        risk_preference=0.5,
        time_horizon=0.5,
        cultural_identity="balanced",
    )
    
    total = (
        new_intent.growth_weight
        + new_intent.profitability_weight
        + new_intent.innovation_weight
        + new_intent.stability_weight
    )
    assert abs(total - 1.0) < 0.01


def test_analyze_intent(service):
    """Test analyzing intent"""
    # First, set an intent
    service.set_intent(
        growth_weight=0.35,
        profitability_weight=0.25,
        innovation_weight=0.25,
        stability_weight=0.15,
        risk_preference=0.6,
        time_horizon=0.7,
        cultural_identity="innovative",
    )
    
    # Generate multi-objective analysis first
    from src.backend.app.services.multi_objective_service import MultiObjectiveService
    multi_service = MultiObjectiveService()
    multi_service.generate_multi_objective_analysis()
    
    # Now analyze intent
    analysis = service.analyze_intent()
    
    assert analysis is not None
    assert analysis.current_intent is not None
    assert analysis.recommended_strategy_id is not None
    assert analysis.recommended_strategy_score is not None


def test_export_intent_markdown(service):
    """Test exporting intent to markdown"""
    service.set_intent(
        growth_weight=0.35,
        profitability_weight=0.25,
        innovation_weight=0.25,
        stability_weight=0.15,
        risk_preference=0.6,
        time_horizon=0.7,
        cultural_identity="innovative",
    )
    
    md = service.export_intent_to_markdown()
    
    assert "企業意思" in md
    assert "35" in md  # growth_weight 0.35
    assert "innovative" in md
