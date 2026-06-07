import pytest
from src.backend.app.models.autonomous_model import AutonomousCycleResult
from src.backend.app.models.executive_agent_model import (
    ExecutiveRole,
    AgentVote,
    ExecutiveDecisionResult,
)
from src.backend.app.services.autonomous_enterprise_service import AutonomousEnterpriseService
from src.backend.app.services.executive_agent_service import ExecutiveAgentService
from src.backend.app.models.self_optimization_model import OptimizationObjective


class TestAutonomousLoopWithAgents:
    """Autonomous Loop と Executive Agents の統合テスト"""
    
    def setup_method(self):
        self.autonomous_service = AutonomousEnterpriseService()
        self.agent_service = ExecutiveAgentService()
    
    def test_autonomous_cycle_includes_executive_decision(self):
        """自律サイクルに Executive Decision が含まれる"""
        # Note: 実際の実行には多くの依存サービスが必要なため、
        # ここではモデル構造のテストに焦点
        
        # ダミーの ExecutiveDecisionResult を作成
        votes = [
            AgentVote(
                role=ExecutiveRole.CEO,
                candidate_id="strategy_1",
                score=0.85,
                rationale="test"
            ),
            AgentVote(
                role=ExecutiveRole.CFO,
                candidate_id="strategy_2",
                score=0.78,
                rationale="test"
            ),
        ]
        
        decision = ExecutiveDecisionResult(
            selected_candidate_id="strategy_1",
            selected_candidate_desc="Growth Strategy",
            votes=votes,
            aggregated_score=0.83,
            method="weighted_average",
        )
        
        # AutonomousCycleResult に decision を含められることを確認
        cycle = AutonomousCycleResult(
            cycle_id=1,
            objective=OptimizationObjective.GROWTH,
            previous_evolution_score=0.65,
            new_evolution_score=0.72,
            evolution_score_change=0.07,
            cycle_summary="Test cycle",
            executive_decision=decision,  # Step AC: Executive decision
        )
        
        assert cycle.executive_decision is not None
        assert cycle.executive_decision.selected_candidate_id == "strategy_1"
        assert len(cycle.executive_decision.votes) == 2
    
    def test_cycle_summary_includes_executive_context(self):
        """サイクルサマリーに Executive 情報が含まれる"""
        votes = [
            AgentVote(role=ExecutiveRole.CEO, candidate_id="A", score=0.9, rationale="high risk"),
            AgentVote(role=ExecutiveRole.CFO, candidate_id="B", score=0.7, rationale="low cost"),
        ]
        
        decision = ExecutiveDecisionResult(
            selected_candidate_id="A",
            selected_candidate_desc="Aggressive Growth",
            votes=votes,
            aggregated_score=0.85,
            method="weighted_average",
            supporting_roles=["CEO"],
            opposing_roles=["CFO"],
        )
        
        cycle = AutonomousCycleResult(
            cycle_id=1,
            objective=OptimizationObjective.GROWTH,
            previous_evolution_score=0.65,
            new_evolution_score=0.75,
            evolution_score_change=0.10,
            cycle_summary=f"Selected A with support from CEO (opposing: CFO)",
            executive_decision=decision,
        )
        
        assert "CEO" in cycle.cycle_summary
        assert decision.selected_candidate_id in cycle.cycle_summary


class TestIntentLearningWithAgents:
    """Corporate Intent の Agent 統合学習テスト"""
    
    def test_intent_learning_incorporates_agent_votes(self):
        """Intent 学習にエージェント投票が反映される"""
        # 複数サイクルの実行結果を想定
        from src.backend.app.services.intent_learning_with_agents import (
            update_intent_from_executive_decisions
        )
        from src.backend.app.models.corporate_intent_model import CorporateIntent
        
        # ダミーサイクルデータ
        cycles = []
        for i in range(3):
            votes = [
                AgentVote(role=ExecutiveRole.CFO, candidate_id=f"s{i}", 
                         score=0.8, rationale="stability and profitability"),
                AgentVote(role=ExecutiveRole.CTO, candidate_id=f"s{i}", 
                         score=0.7, rationale="innovation opportunity"),
            ]
            decision = ExecutiveDecisionResult(
                selected_candidate_id=f"s{i}",
                selected_candidate_desc=f"Strategy {i}",
                votes=votes,
                aggregated_score=0.75,
                method="weighted_average",
            )
            cycle = AutonomousCycleResult(
                cycle_id=i,
                objective=OptimizationObjective.PROFITABILITY,
                previous_evolution_score=0.6 + i*0.05,
                new_evolution_score=0.65 + i*0.05,
                evolution_score_change=0.05,
                cycle_summary="Test",
                executive_decision=decision,
            )
            cycles.append(cycle)
        
        # Intent 学習を実行
        learning = update_intent_from_executive_decisions(
            CorporateIntent(),
            cycles
        )
        
        assert learning.cycle_count == 3
        assert learning.learning_confidence > 0
        assert learning.avg_profitability > 0  # CFO の推す profitability が増加


class TestAutonomousExecutiveSummary:
    """自律ループ × Executive の統合サマリテスト"""
    
    def test_autonomous_executive_summary_generation(self):
        """自律ループの Executive 統合サマリー生成"""
        
        votes = [
            AgentVote(role=ExecutiveRole.CEO, candidate_id="growth", score=0.88, rationale="long-term value"),
            AgentVote(role=ExecutiveRole.CFO, candidate_id="profit", score=0.82, rationale="cash generation"),
            AgentVote(role=ExecutiveRole.CMO, candidate_id="growth", score=0.85, rationale="market expansion"),
            AgentVote(role=ExecutiveRole.CTO, candidate_id="innovation", score=0.80, rationale="tech advancement"),
            AgentVote(role=ExecutiveRole.CHRO, candidate_id="stability", score=0.75, rationale="org stability"),
        ]
        
        decision = ExecutiveDecisionResult(
            selected_candidate_id="growth",
            selected_candidate_desc="Growth-focused strategy",
            votes=votes,
            aggregated_score=0.86,
            method="weighted_average",
            supporting_roles=["CEO", "CMO"],
            opposing_roles=["CHRO"],
        )
        
        # Summary 情報の検証
        assert decision.selected_candidate_id == "growth"
        assert len(decision.supporting_roles) == 2
        assert len(decision.opposing_roles) == 1
        assert decision.aggregated_score > 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])