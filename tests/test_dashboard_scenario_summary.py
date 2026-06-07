import pytest
from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService
from src.backend.app.models.executive_dashboard_model import ScenarioSummary
from src.backend.app.models.scenario_model import ScenarioType


def test_get_scenario_summaries():
    \"\"\"シナリオサマリー取得のテスト\"\"\"
    service = ExecutiveDashboardService()
    
    # シナリオ実行サービスがデータを生成している前提
    summaries = service._get_scenario_summaries()
    
    assert isinstance(summaries, list)
    assert len(summaries) == 5  # 5つのシナリオタイプ
    
    # 各サマリーの構造確認
    for summary in summaries:
        assert isinstance(summary, ScenarioSummary)
        assert summary.scenario_type in [t.value for t in ScenarioType]
        assert isinstance(summary.description, str)
        assert isinstance(summary.risk_level, str)
        assert isinstance(summary.opportunity_level, str)
        assert isinstance(summary.evolution_score, float)
        assert 0.0 <= summary.evolution_score <= 1.0


def test_scenario_summary_fields():
    \"\"\"シナリオサマリーフィールドのテスト\"\"\"
    service = ExecutiveDashboardService()
    
    summaries = service._get_scenario_summaries()
    
    for summary in summaries:
        # 必須フィールドの確認
        assert hasattr(summary, 'scenario_type')
        assert hasattr(summary, 'description')
        assert hasattr(summary, 'risk_level')
        assert hasattr(summary, 'opportunity_level')
        assert hasattr(summary, 'evolution_score')
        assert hasattr(summary, 'key_changes')
        
        # データ型の確認
        assert isinstance(summary.scenario_type, str)
        assert isinstance(summary.description, str)
        assert isinstance(summary.risk_level, str)
        assert isinstance(summary.opportunity_level, str)
        assert isinstance(summary.evolution_score, float)
        assert isinstance(summary.key_changes, list)
        
        # risk_level と opportunity_level の値確認
        assert summary.risk_level in ["Low", "Medium", "High"]
        assert summary.opportunity_level in ["Low", "Medium", "High"]
        
        # evolution_score の範囲確認
        assert 0.0 <= summary.evolution_score <= 1.0
        
        # key_changes の各要素が文字列か確認
        for change in summary.key_changes:
            assert isinstance(change, str)


def test_scenario_summary_uniqueness():
    \"\"\"シナリオサマリーの一意性のテスト\"\"\"
    service = ExecutiveDashboardService()
    
    summaries = service._get_scenario_summaries()
    
    # scenario_type が一意か確認
    scenario_types = [s.scenario_type for s in summaries]
    assert len(scenario_types) == len(set(scenario_types))
    
    # 全てのScenarioTypeが含まれているか確認
    expected_types = {t.value for t in ScenarioType}
    actual_types = set(scenario_types)
    assert expected_types == actual_types


def test_scenario_summary_content():
    \"\"\"シナリオサマリーの内容テスト\"\"\"
    service = ExecutiveDashboardService()
    
    summaries = service._get_scenario_summaries()
    
    # 各シナリオタイプの説明が適切か確認
    descriptions = {s.scenario_type: s.description for s in summaries}
    
    assert "baseline" in descriptions
    assert "optimistic" in descriptions
    assert "pessimistic" in descriptions
    assert "tech_boom" in descriptions
    assert "recession" in descriptions
    
    # 説明が空でないか確認
    for desc in descriptions.values():
        assert len(desc.strip()) > 0
    
    # key_changes が空でないか確認
    for summary in summaries:
        assert len(summary.key_changes) > 0
        for change in summary.key_changes:
            assert len(change.strip()) > 0


def test_scenario_summary_risk_opportunity_logic():
    \"\"\"リスク・機会評価のロジックテスト\"\"\"
    service = ExecutiveDashboardService()
    
    summaries = service._get_scenario_summaries()
    
    # 楽観的シナリオは機会が高く、リスクが低いはず
    optimistic = next(s for s in summaries if s.scenario_type == "optimistic")
    assert optimistic.opportunity_level == "High"
    assert optimistic.risk_level in ["Low", "Medium"]
    
    # 悲観的シナリオはリスクが高く、機会が低いはず
    pessimistic = next(s for s in summaries if s.scenario_type == "pessimistic")
    assert pessimistic.risk_level == "High"
    assert pessimistic.opportunity_level in ["Low", "Medium"]
    
    # 不況シナリオはリスクが高く、機会が低いはず
    recession = next(s for s in summaries if s.scenario_type == "recession")
    assert recession.risk_level == "High"
    assert recession.opportunity_level in ["Low", "Medium"]
    
    # 技術ブームシナリオは機会が高く、リスクが中程度のはず
    tech_boom = next(s for s in summaries if s.scenario_type == "tech_boom")
    assert tech_boom.opportunity_level in ["Medium", "High"]
    assert tech_boom.risk_level in ["Low", "Medium", "High"]


def test_evolution_score_range():
    \"\"\"進化スコア範囲のテスト\"\"\"
    service = ExecutiveDashboardService()
    
    summaries = service._get_scenario_summaries()
    
    for summary in summaries:
        # 進化スコアが0.0-1.0の範囲内か確認
        assert 0.0 <= summary.evolution_score <= 1.0
        
        # 小数点以下2桁までか確認（オプション）
        # score_str = f"{summary.evolution_score:.2f}"
        # assert str(summary.evolution_score) == score_str


def test_dashboard_integration():
    \"\"\"ダッシュボード統合のテスト\"\"\"
    service = ExecutiveDashboardService()
    
    # ダッシュボードデータを取得
    dashboard_data = service.get_executive_dashboard()
    
    # scenarios フィールドが存在するか確認
    assert "scenarios" in dashboard_data
    assert isinstance(dashboard_data["scenarios"], list)
    assert len(dashboard_data["scenarios"]) == 5
    
    # 各シナリオが正しい構造か確認
    for scenario in dashboard_data["scenarios"]:
        assert "scenario_type" in scenario
        assert "description" in scenario
        assert "risk_level" in scenario
        assert "opportunity_level" in scenario
        assert "evolution_score" in scenario
        assert "key_changes" in scenario


def test_scenario_summary_data_types():
    \"\"\"シナリオサマリーデータ型のテスト\"\"\"
    service = ExecutiveDashboardService()
    
    summaries = service._get_scenario_summaries()
    
    for summary in summaries:
        # Pydanticモデルのフィールド型確認
        assert isinstance(summary.scenario_type, str)
        assert isinstance(summary.description, str)
        assert isinstance(summary.risk_level, str)
        assert isinstance(summary.opportunity_level, str)
        assert isinstance(summary.evolution_score, float)
        assert isinstance(summary.key_changes, list)
        
        # key_changes の要素型確認
        for change in summary.key_changes:
            assert isinstance(change, str)
