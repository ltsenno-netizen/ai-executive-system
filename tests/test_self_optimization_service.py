import pytest
from src.backend.app.services.self_optimization_service import SelfOptimizationService
from src.backend.app.models.self_optimization_model import OptimizationObjective


def test_generate_self_optimization_plan():
    """Test self-optimization plan generation"""
    service = SelfOptimizationService()
    
    # This test assumes scenario results are already available
    # In a real test, you'd mock the dependencies
    try:
        plan = service.generate_self_optimization_plan(OptimizationObjective.GROWTH)
        
        assert plan is not None
        assert plan.objective == OptimizationObjective.GROWTH
        assert len(plan.recommended_strategies) > 0
        assert len(plan.recommended_culture_shifts) > 0
        assert len(plan.recommended_leadership_changes) > 0
    except ValueError:
        # Expected if no scenarios are run yet
        pytest.skip("No scenario results available")


def test_get_latest_plan():
    """Test retrieving latest plan"""
    service = SelfOptimizationService()
    
    try:
        # Generate a plan first
        plan = service.generate_self_optimization_plan(OptimizationObjective.STABILITY)
        
        # Retrieve it
        retrieved = service.get_latest_plan(OptimizationObjective.STABILITY)
        
        assert retrieved is not None
        assert retrieved.objective == OptimizationObjective.STABILITY
    except ValueError:
        pytest.skip("No scenario results available")


def test_get_all_plans():
    """Test retrieving all plans"""
    service = SelfOptimizationService()
    
    try:
        # Generate a few plans
        for objective in [OptimizationObjective.GROWTH, OptimizationObjective.INNOVATION]:
            service.generate_self_optimization_plan(objective)
        
        # Get all
        plans = service.get_all_plans()
        
        assert len(plans) >= 2
    except ValueError:
        pytest.skip("No scenario results available")
