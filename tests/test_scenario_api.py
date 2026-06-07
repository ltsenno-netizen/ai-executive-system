import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app
from src.backend.app.models.scenario_model import ScenarioType


client = TestClient(app)


def test_run_scenarios_endpoint():
    \"\"\"シナリオ実行APIのテスト\"\"\"
    response = client.post("/api/scenarios/run")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "results" in data
    assert len(data["results"]) == 5
    
    # 各結果の構造確認
    for result in data["results"]:
        assert "scenario_type" in result
        assert "projected_culture" in result
        assert "projected_financials" in result
        assert "projected_evolution_score" in result
        assert "risk_assessment" in result
        assert "opportunity_assessment" in result


def test_get_latest_scenarios_endpoint():
    \"\"\"最新シナリオ取得APIのテスト\"\"\"
    # まず実行
    client.post("/api/scenarios/run")
    
    # 取得
    response = client.get("/api/scenarios/latest")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "scenarios" in data
    assert len(data["scenarios"]) == 5
    
    # 各シナリオの構造確認
    for scenario in data["scenarios"]:
        assert "scenario_type" in scenario
        assert "description" in scenario
        assert "projected_culture" in scenario
        assert "projected_financials" in scenario
        assert "risk_assessment" in scenario
        assert "opportunity_assessment" in scenario


def test_get_scenario_by_type_endpoint():
    \"\"\"シナリオタイプ別取得APIのテスト\"\"\"
    # まず実行
    client.post("/api/scenarios/run")
    
    # 各タイプで取得
    for scenario_type in ScenarioType:
        response = client.get(f"/api/scenarios/{scenario_type.value}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["scenario_type"] == scenario_type.value
        assert "projected_culture" in data
        assert "projected_financials" in data
        assert "projected_evolution_score" in data
        assert "risk_assessment" in data
        assert "opportunity_assessment" in data


def test_get_nonexistent_scenario():
    \"\"\"存在しないシナリオ取得のテスト\"\"\"
    response = client.get("/api/scenarios/nonexistent")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_scenario_response_structure():
    \"\"\"APIレスポンス構造のテスト\"\"\"
    # 実行
    client.post("/api/scenarios/run")
    
    response = client.get("/api/scenarios/baseline")
    assert response.status_code == 200
    data = response.json()
    
    # 必須フィールドの確認
    required_fields = [
        'scenario_type', 'description', 'duration_months',
        'projected_culture', 'projected_environment', 'projected_executive_team',
        'projected_financials', 'projected_evolution_score',
        'risk_assessment', 'opportunity_assessment', 'created_at'
    ]
    
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    
    # projected_culture の構造確認
    culture = data['projected_culture']
    culture_fields = [
        'period', 'innovation_culture', 'people_culture', 'process_culture',
        'market_culture', 'aggressiveness_culture', 'risk_aversion_culture',
        'brand_culture', 'cost_culture', 'execution_culture', 'stability_culture'
    ]
    
    for field in culture_fields:
        assert field in culture, f"Missing culture field: {field}"
    
    # projected_financials の構造確認
    financials = data['projected_financials']
    financial_fields = ['revenue', 'profit', 'cash']
    
    for field in financial_fields:
        assert field in financials, f"Missing financial field: {field}"
        assert isinstance(financials[field], (int, float)), f"Financial field {field} should be numeric"


def test_scenario_run_response_format():
    \"\"\"シナリオ実行レスポンス形式のテスト\"\"\"
    response = client.post("/api/scenarios/run")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data["message"], str)
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 5
    
    # 各結果が辞書形式か確認
    for result in data["results"]:
        assert isinstance(result, dict)
        assert "scenario_type" in result


def test_api_error_handling():
    \"\"\"APIエラーハンドリングのテスト\"\"\"
    # 存在しないエンドポイント
    response = client.get("/api/scenarios/invalid")
    assert response.status_code == 404
    
    # 無効なメソッド
    response = client.put("/api/scenarios/run")
    assert response.status_code == 405


def test_scenario_data_consistency():
    \"\"\"シナリオデータの整合性テスト\"\"\"
    # 実行
    run_response = client.post("/api/scenarios/run")
    assert run_response.status_code == 200
    
    # 最新取得
    latest_response = client.get("/api/scenarios/latest")
    assert latest_response.status_code == 200
    
    run_data = run_response.json()["results"]
    latest_data = latest_response.json()["scenarios"]
    
    # データが一致するか確認
    assert len(run_data) == len(latest_data)
    
    # scenario_type でソートして比較
    run_sorted = sorted(run_data, key=lambda x: x["scenario_type"])
    latest_sorted = sorted(latest_data, key=lambda x: x["scenario_type"])
    
    for run_item, latest_item in zip(run_sorted, latest_sorted):
        assert run_item["scenario_type"] == latest_item["scenario_type"]
        assert run_item["projected_evolution_score"] == latest_item["projected_evolution_score"]
        assert run_item["risk_assessment"] == latest_item["risk_assessment"]
        assert run_item["opportunity_assessment"] == latest_item["opportunity_assessment"]
