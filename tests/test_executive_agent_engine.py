import pytest
from src.backend.app.models.executive_agent_model import (
    ExecutiveRole,
    ExecutiveAgentConfig,
    AgentVote,
    ExecutiveDecisionResult,
)
from src.backend.app.services.executive_agent_engine import (
    score_candidate_for_agent,
    aggregate_votes,
    run_executive_council,
    get_default_role_weights,
    calculate_consensus_level,
)
from src.backend.app.models.multi_objective_model import (
    StrategyCandidate,
    ObjectiveVector,
)


def create_test_candidate(
    scenario_type: str = "growth",
    optimization_objective: str = "max_growth",
    growth: float = 100.0,
    profitability: float = 15.0,
    innovation: float = 0.8,
    stability: float = 0.7,
) -> StrategyCandidate:
    """テスト用候補を作成"""
    return StrategyCandidate(
        id=f"candidate_{scenario_type}_{optimization_objective}",
        scenario_type=scenario_type,
        optimization_objective=optimization_objective,
        objective_vector=ObjectiveVector(
            growth=growth,
            profitability=profitability,
            innovation=innovation,
            stability=stability,
        ),
        risk_index=0.5,
        estimated_cost=0.5,
        people_impact_score=0.5,
        technology_impact_score=0.5,
        market_impact_score=0.5,
    )


def create_test_agent(
    role: ExecutiveRole = ExecutiveRole.CEO,
    growth_weight: float = 0.3,
    profitability_weight: float = 0.25,
    innovation_weight: float = 0.25,
    stability_weight: float = 0.2,
    risk_aversion: float = 0.5,
) -> ExecutiveAgentConfig:
    """テスト用エージェントを作成"""
    return ExecutiveAgentConfig(
        role=role,
        name=f"{role.value} Agent",
        growth_weight=growth_weight,
        profitability_weight=profitability_weight,
        innovation_weight=innovation_weight,
        stability_weight=stability_weight,
        risk_aversion=risk_aversion,
        cost_sensitivity=0.5,
        people_focus=0.5,
        technology_focus=0.5,
        market_focus=0.5,
        vote_weight=1.0,
        focus_area="Test focus",
        concerns=["Test concern"],
    )


class TestExecutiveAgentModel:
    """Executive Agent モデルのテスト"""
    
    def test_executive_role_enum(self):
        """ロール列挙型のテスト"""
        assert ExecutiveRole.CEO.value == "CEO"
        assert ExecutiveRole.CFO.value == "CFO"
        assert ExecutiveRole.CMO.value == "CMO"
        assert ExecutiveRole.CTO.value == "CTO"
        assert ExecutiveRole.CHRO.value == "CHRO"
    
    def test_executive_agent_config_creation(self):
        """エージェント設定の作成"""
        agent = ExecutiveAgentConfig(
            role=ExecutiveRole.CEO,
            name="Test CEO",
            growth_weight=0.3,
            profitability_weight=0.3,
            innovation_weight=0.2,
            stability_weight=0.2,
            risk_aversion=0.5,
        )
        
        assert agent.role == ExecutiveRole.CEO
        assert agent.name == "Test CEO"
        assert agent.growth_weight == 0.3
    
    def test_agent_vote_creation(self):
        """投票の作成"""
        vote = AgentVote(
            role=ExecutiveRole.CEO,
            candidate_id="test_candidate",
            score=0.85,
            rationale="Test rationale",
        )
        
        assert vote.role == ExecutiveRole.CEO
        assert vote.candidate_id == "test_candidate"
        assert vote.score == 0.85
    
    def test_executive_decision_result_creation(self):
        """決定結果の作成"""
        votes = [
            AgentVote(
                role=ExecutiveRole.CEO,
                candidate_id="candidate_1",
                score=0.8,
                rationale="test",
            )
        ]
        
        result = ExecutiveDecisionResult(
            selected_candidate_id="candidate_1",
            selected_candidate_desc="Candidate 1",
            votes=votes,
            aggregated_score=0.8,
            method="weighted_average",
        )
        
        assert result.selected_candidate_id == "candidate_1"
        assert result.method == "weighted_average"


class TestExecutiveAgentEngine:
    """Executive Agent Engine のテスト"""
    
    def test_score_candidate_for_agent(self):
        """エージェントによる候補スコアリング"""
        agent = create_test_agent(ExecutiveRole.CFO, profitability_weight=0.4)
        candidate = create_test_candidate(profitability=20.0)
        
        vote = score_candidate_for_agent(agent, candidate)
        
        assert vote.role == ExecutiveRole.CFO
        assert vote.candidate_id is not None
        assert vote.score > 0
        assert "base=" in vote.rationale
    
    def test_aggregate_votes(self):
        """投票集約"""
        votes = [
            AgentVote(role=ExecutiveRole.CEO, candidate_id="A", score=0.8, rationale="test"),
            AgentVote(role=ExecutiveRole.CFO, candidate_id="A", score=0.7, rationale="test"),
            AgentVote(role=ExecutiveRole.CMO, candidate_id="B", score=0.9, rationale="test"),
        ]
        
        role_weights = {
            ExecutiveRole.CEO: 1.5,
            ExecutiveRole.CFO: 1.2,
            ExecutiveRole.CMO: 1.0,
        }
        
        result = aggregate_votes(votes, role_weights)
        
        assert result.selected_candidate_id in ["A", "B"]
        assert result.aggregated_score > 0
        assert result.method == "weighted_average"
    
    def test_run_executive_council(self):
        """経営会議の実行"""
        agents = [
            create_test_agent(ExecutiveRole.CEO),
            create_test_agent(ExecutiveRole.CFO),
        ]
        
        candidates = [
            create_test_candidate("growth", "max_growth"),
            create_test_candidate("profit", "max_profit"),
        ]
        
        role_weights = get_default_role_weights()
        
        result = run_executive_council(agents, candidates, role_weights)
        
        assert result.selected_candidate_id is not None
        assert len(result.votes) > 0
        assert result.aggregated_score > 0
    
    def test_get_default_role_weights(self):
        """デフォルト投票重み"""
        weights = get_default_role_weights()
        
        assert ExecutiveRole.CEO in weights
        assert weights[ExecutiveRole.CEO] == 1.5  # CEO は重み付け
        assert weights[ExecutiveRole.CFO] == 1.2
    
    def test_calculate_consensus_level(self):
        """合意度計算"""
        votes = [
            AgentVote(role=ExecutiveRole.CEO, candidate_id="A", score=0.9, rationale="test"),
            AgentVote(role=ExecutiveRole.CFO, candidate_id="A", score=0.8, rationale="test"),
            AgentVote(role=ExecutiveRole.CMO, candidate_id="A", score=0.85, rationale="test"),
        ]
        
        role_weights = get_default_role_weights()
        
        consensus = calculate_consensus_level(votes, role_weights)
        
        assert consensus in ["high", "medium", "low"]


class TestExecutiveAgentScoring:
    """エージェント別スコアリングのテスト"""
    
    def test_ceo_perspective(self):
        """CEO の視点 - バランスの取れた評価"""
        ceo = create_test_agent(ExecutiveRole.CEO, growth_weight=0.3)
        candidate = create_test_candidate(growth=120.0, profitability=18.0)
        
        vote = score_candidate_for_agent(ceo, candidate)
        
        assert vote.score > 0
    
    def test_cfo_perspective(self):
        """CFO の視点 - 収益性・リスク重視"""
        cfo = create_test_agent(
            ExecutiveRole.CFO,
            profitability_weight=0.4,
            risk_aversion=0.7
        )
        candidate = create_test_candidate(profitability=20.0, stability=0.8)
        
        vote = score_candidate_for_agent(cfo, candidate)
        
        assert vote.score > 0
    
    def test_chro_perspective(self):
        """CHRO の視点 - 人材重視"""
        chro = create_test_agent(
            ExecutiveRole.CHRO,
            people_focus=0.9
        )
        candidate = create_test_candidate()
        
        vote = score_candidate_for_agent(chro, candidate)
        
        # people_focus によるボーナスが発生
        assert "people_bonus" in vote.breakdown


if __name__ == "__main__":
    pytest.main([__file__, "-v"])