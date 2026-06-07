import pytest
import os
import json
from src.backend.app.services.scenario_service import ScenarioService
from src.backend.app.models.scenario_model import ScenarioType


def test_run_all_scenarios():
    """Test running all scenarios"""
    service = ScenarioService()
    
    # Execute
    results = service.run_all_scenarios()
    
    # Verify
    assert len(results) == 5
    assert all(isinstance(r, dict) for r in results)
    assert all('scenario_type' in r for r in results)
    assert all('projected_culture' in r for r in results)
    assert all('projected_financials' in r for r in results)
    assert all('projected_evolution_score' in r for r in results)
    assert all('risk_assessment' in r for r in results)
    assert all('opportunity_assessment' in r for r in results)


def test_get_scenario_result():
    """Test scenario result retrieval"""
    service = ScenarioService()
    
    # Execute first to save data
    service.run_all_scenarios()
    
    # Get each scenario type
    for scenario_type in ScenarioType:
        result = service.get_scenario_result(scenario_type)
        assert result is not None
        assert result['scenario_type'] == scenario_type.value
        assert 'projected_culture' in result
        assert 'projected_financials' in result
        assert 'projected_evolution_score' in result
        assert 'risk_assessment' in result
        assert 'opportunity_assessment' in result


def test_data_persistence():
    """Test data persistence"""
    service = ScenarioService()
    
    # Execute
    results = service.run_all_scenarios()
    
    # Check data is saved
    data_dir = "data/scenarios"
    assert os.path.exists(data_dir)
    
    for scenario_type in ScenarioType:
        file_path = os.path.join(data_dir, f"{scenario_type.value}.json")
        assert os.path.exists(file_path)
        
        # Check JSON readable
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'scenario_type' in data
            assert data['scenario_type'] == scenario_type.value


def test_get_all_scenario_results():
    """Test getting all scenario results"""
    service = ScenarioService()
    
    # Execute
    service.run_all_scenarios()
    
    # Get all results
    all_results = service.get_all_scenario_results()
    
    assert len(all_results) == 5
    assert all(isinstance(r, dict) for r in all_results)
    
    # Check all scenario types included
    scenario_types = [r['scenario_type'] for r in all_results]
    assert 'baseline' in scenario_types
    assert 'optimistic' in scenario_types
    assert 'pessimistic' in scenario_types
    assert 'tech_boom' in scenario_types
    assert 'recession' in scenario_types


def test_scenario_result_structure():
    """Test scenario result structure"""
    service = ScenarioService()
    
    # Execute
    service.run_all_scenarios()
    
    result = service.get_scenario_result(ScenarioType.BASELINE)
    
    # Check required fields
    required_fields = [
        'scenario_type', 'description', 'duration_months',
        'projected_culture', 'projected_environment', 'projected_executive_team',
        'projected_financials', 'projected_evolution_score',
        'risk_assessment', 'opportunity_assessment', 'created_at'
    ]
    
    for field in required_fields:
        assert field in result, f"Missing field: {field}"
    
    # Check projected_culture structure
    culture = result['projected_culture']
    culture_fields = [
        'period', 'innovation_culture', 'people_culture', 'process_culture',
        'market_culture', 'aggressiveness_culture', 'risk_aversion_culture',
        'brand_culture', 'cost_culture', 'execution_culture', 'stability_culture'
    ]
    
    for field in culture_fields:
        assert field in culture, f"Missing culture field: {field}"
    
    # Check projected_financials structure
    financials = result['projected_financials']
    financial_fields = ['revenue', 'profit', 'cash']
    
    for field in financial_fields:
        assert field in financials, f"Missing financial field: {field}"
        assert isinstance(financials[field], (int, float)), f"Financial field {field} should be numeric"


def test_scenario_execution_time():
    """Test scenario execution time"""
    import time
    
    service = ScenarioService()
    
    start_time = time.time()
    results = service.run_all_scenarios()
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Check execution time is reasonable (within 5 seconds)
    assert execution_time < 5.0, f"Execution took too long: {execution_time} seconds"
    
    # Check results generated correctly
    assert len(results) == 5
