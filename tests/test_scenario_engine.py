import pytest
from src.backend.app.services.scenario_engine import ScenarioEngine
from src.backend.app.models.scenario_model import ScenarioType, ScenarioDefinition
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.external_environment_model_v2 import ExternalEnvironmentState, PESTFactors, Competitor


def test_generate_scenario_definitions():
    """Test scenario definition generation"""
    engine = ScenarioEngine()
    definitions = engine.generate_scenario_definitions()
    
    assert len(definitions) == 5
    assert any(d.scenario_type == ScenarioType.BASELINE for d in definitions)
    assert any(d.scenario_type == ScenarioType.OPTIMISTIC for d in definitions)
    assert any(d.scenario_type == ScenarioType.PESSIMISTIC for d in definitions)
    assert any(d.scenario_type == ScenarioType.TECH_BOOM for d in definitions)
    assert any(d.scenario_type == ScenarioType.RECESSION for d in definitions)


def test_run_scenario():
    """Test scenario execution"""
    engine = ScenarioEngine()
    
    # テストシナリオ
    scenario = ScenarioDefinition(
        scenario_type=ScenarioType.OPTIMISTIC,
        description="Test optimistic scenario",
        duration_months=36,
        environment_modifiers={"economic": 0.1, "technological": 0.1}
    )
    
    # テストデータ
    current_culture = CultureProfile(
        period="2026-01",
        innovation_culture=0.5,
        people_culture=0.5,
        process_culture=0.5,
        market_culture=0.5,
        aggressiveness_culture=0.5,
        risk_aversion_culture=0.5,
        brand_culture=0.5,
        cost_culture=0.5,
        execution_culture=0.5,
        stability_culture=0.5,
    )
    
    current_environment = ExternalEnvironmentState(
        period="2026-01",
        pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.5),
        competitors=[Competitor(name="Competitor A", aggressiveness=0.5, market_share=0.3)],
        shocks=[],
        market_growth_modifier=0.02,
        risk_modifier=0.0
    )
    
    current_executive_team = {}
    current_financials = {'revenue': 1000000, 'profit': 100000, 'cash': 5000000}
    
    # 実行
    result = engine.run_scenario(
        scenario, current_culture, current_environment,
        current_executive_team, current_financials
    )
    
    # 検証
    assert result.scenario_type == ScenarioType.OPTIMISTIC
    assert isinstance(result.projected_culture, CultureProfile)
    assert isinstance(result.projected_financials, dict)
    assert 'revenue' in result.projected_financials
    assert 'profit' in result.projected_financials
    assert 'cash' in result.projected_financials
    assert isinstance(result.projected_evolution_score, float)
    assert result.risk_assessment in ["Low", "Medium", "High"]
    assert result.opportunity_assessment in ["Low", "Medium", "High"]


def test_environment_modifiers_applied():
    \"\"\"環境modifierが適用されるテスト\"\"\"
    engine = ScenarioEngine()
    
    scenario = ScenarioDefinition(
        scenario_type=ScenarioType.TECH_BOOM,
        description="Tech boom test",
        duration_months=36,
        environment_modifiers={"technological": 0.25}
    )
    
    current_env = ExternalEnvironmentState(
        period="2026-01",
        pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.5),
        competitors=[Competitor(name="Competitor A", aggressiveness=0.5, market_share=0.3)],
        shocks=[],
        market_growth_modifier=0.02,
        risk_modifier=0.0
    )
    
    projected_env = engine._project_environment(current_env, scenario.environment_modifiers)
    
    # technological が +0.25 されているはず
    assert projected_env.pest.technological == min(1.0, 0.5 + 0.25)


def test_culture_projection():
    \"\"\"文化予測のテスト\"\"\"
    engine = ScenarioEngine()
    
    current_culture = CultureProfile(
        period="2026-01",
        innovation_culture=0.5,
        people_culture=0.5,
        process_culture=0.5,
        market_culture=0.5,
        aggressiveness_culture=0.5,
        risk_aversion_culture=0.5,
        brand_culture=0.5,
        cost_culture=0.5,
        execution_culture=0.5,
        stability_culture=0.5,
    )
    
    # 技術進展環境
    projected_env = ExternalEnvironmentState(
        period="2026-01",
        pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.8),
        competitors=[Competitor(name="Competitor A", aggressiveness=0.5, market_share=0.3)],
        shocks=[],
        market_growth_modifier=0.02,
        risk_modifier=0.0
    )
    
    projected_culture = engine._project_culture(current_culture, projected_env)
    
    # innovation_culture が増加しているはず
    assert projected_culture.innovation_culture > current_culture.innovation_culture


def test_financial_projection():
    \"\"\"財務予測のテスト\"\"\"
    engine = ScenarioEngine()
    
    current_financials = {'revenue': 1000000, 'profit': 100000, 'cash': 5000000}
    
    projected_env = ExternalEnvironmentState(
        period="2026-01",
        pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.5),
        competitors=[Competitor(name="Competitor A", aggressiveness=0.5, market_share=0.3)],
        shocks=[],
        market_growth_modifier=0.05,  # 成長率5%
        risk_modifier=0.0
    )
    
    projected_financials = engine._project_financials(current_financials, projected_env, 36)
    
    # 3年後の予測なので成長しているはず
    assert projected_financials['revenue'] > current_financials['revenue']
    assert projected_financials['profit'] > current_financials['profit']
    assert projected_financials['cash'] > current_financials['cash']
