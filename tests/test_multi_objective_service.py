import pytest
from src.backend.app.services.multi_objective_service import MultiObjectiveService


@pytest.fixture
def service():
    return MultiObjectiveService()


def test_generate_multi_objective_analysis(service):
    """Test generating multi-objective analysis"""
    frontier = service.generate_multi_objective_analysis()
    
    assert frontier is not None
    assert frontier.total_candidates > 0
    assert frontier.frontier_count > 0
    assert len(frontier.frontier_indices) == frontier.frontier_count
    assert frontier.best_growth >= 0
    assert frontier.best_profitability >= 0
    assert 0 <= frontier.best_innovation <= 1
    assert 0 <= frontier.best_stability <= 1


def test_get_frontier(service):
    """Test retrieving frontier"""
    # Generate first
    service.generate_multi_objective_analysis()
    
    # Retrieve
    frontier = service.get_frontier()
    
    assert frontier is not None
    assert frontier.frontier_count > 0


def test_get_candidates(service):
    """Test retrieving all candidates"""
    # Generate first
    service.generate_multi_objective_analysis()
    
    # Retrieve
    candidates = service.get_candidates()
    
    assert candidates is not None
    assert len(candidates) > 0


def test_get_frontier_candidates(service):
    """Test retrieving only frontier candidates"""
    # Generate first
    service.generate_multi_objective_analysis()
    
    # Retrieve frontier candidates
    frontier_candidates = service.get_frontier_candidates()
    
    assert frontier_candidates is not None
    assert len(frontier_candidates) > 0
    
    # Get full frontier for comparison
    frontier = service.get_frontier()
    assert len(frontier_candidates) == len(frontier.frontier_indices)
