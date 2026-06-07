import pytest
from src.backend.app.models.corporate_intent_model import CorporateIntent
from src.backend.app.models.autonomous_model import AutonomousCycleResult
from src.backend.app.models.executive_agent_model import (
    ExecutiveRole,
    AgentVote,
    ExecutiveDecisionResult,
)
from src.backend.app.models.self_optimization_model import OptimizationObjective
from src.backend.app.services.intent_learning_with_agents import (
    update_intent_from_executive_decisions,
    apply_learning_to_intent_with_agents,
    _infer_cultural_identity,
)


class TestIntentLearningWithAgents:
    """Corporate Intent の Agent 統合学習テスト"""
    
    def test_update_intent_from_executive_decisions(self):
        """Executive Decision から Intent を学習"""
        
        # 複数サイクルで CFO が profitability を推す場合
        cycles = []
        for i in range(3):
            votes = [
                AgentVote(
                    role=ExecutiveRole.CFO,
                    candidate_id=f"profit_{i}",
                    score=0.85,
                    rationale="profitability and stability focus"
                ),
                AgentVote(
                    role=ExecutiveRole.CTO,
                    candidate_id=f"innovation_{i}",
                    score=0.75,
                    rationale="innovation and growth potential"
                ),
            ]
            
            decision = ExecutiveDecisionResult(
                selected_candidate_id=f"profit_{i}",
                selected_candidate_desc=f"Profit Strategy {i}",
                votes=votes,
                aggregated_score=0.80,
                method="weighted_average",
                supporting_roles=["CFO"],
                opposing_roles=["CTO"],
            )
            
            cycle = AutonomousCycleResult(
                cycle_id=i,
                objective=OptimizationObjective.PROFITABILITY,
                previous_evolution_score=0.60 + i*0.05,
                new_evolution_score=0.65 + i*0.05,
                evolution_score_change=0.05,
                cycle_summary="Profitable cycle",
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
        assert learning.avg_profitability >= 0
    
    def test_apply_learning_to_intent(self):
        """学習結果を Intent に反映"""
        from src.backend.app.models.corporate_intent_model import IntentLearningHistory
        
        current_intent = CorporateIntent(
            growth_weight=0.25,
            profitability_weight=0.25,
            innovation_weight=0.25,
            stability_weight=0.25,
            risk_preference=0.5,
        )
        
        learning = IntentLearningHistory(
            cycle_count=10,
            avg_growth=0.2,
            avg_profitability=0.4,  # CFO推奨
            avg_innovation=0.15,
            avg_stability=0.25,
            avg_risk_taken=0.4,
            risk_volatility=0.1,
            learning_confidence=0.8,
        )
        
        agent_patterns = {
            "CFO": {"profitability": 10, "stability": 8},
            "CTO": {"innovation": 7},
        }
        
        updated_intent = apply_learning_to_intent_with_agents(
            current_intent,
            learning,
            agent_patterns
        )
        
        # 学習により profitability_weight が増加
        assert updated_intent.profitability_weight > current_intent.profitability_weight
        assert updated_intent.growth_weight < current_intent.growth_weight  # 減少
    
    def test_cultural_identity_inference(self):
        """重みから企業文化的アイデンティティを推定"""
        
        # 革新重視
        identity = _infer_cultural_identity(0.2, 0.2, 0.5, 0.1)
        assert identity == "innovative"
        
        # 安定重視
        identity = _infer_cultural_identity(0.2, 0.2, 0.1, 0.5)
        assert identity == "stable"
        
        # 成長重視
        identity = _infer_cultural_identity(0.5, 0.2, 0.2, 0.1)
        assert identity == "aggressive"
        
        # 収益性重視
        identity = _infer_cultural_identity(0.2, 0.5, 0.2, 0.1)
        assert identity == "conservative"
        
        # バランス型
        identity = _infer_cultural_identity(0.25, 0.25, 0.25, 0.25)
        assert identity == "balanced"
    
    def test_learning_confidence_calculation(self):
        """学習信頼度の計算"""
        
        # 少数サイクルでは低信頼度
        cycles_few = [
            AutonomousCycleResult(
                cycle_id=i,
                objective=OptimizationObjective.GROWTH,
                previous_evolution_score=0.6,
                new_evolution_score=0.65,
                evolution_score_change=0.05 if i % 2 == 0 else -0.02,
                cycle_summary="Test",
                executive_decision=None,
            )
            for i in range(2)
        ]
        
        learning_few = update_intent_from_executive_decisions(
            CorporateIntent(),
            cycles_few
        )
        
        # 多数サイクルで高信頼度
        cycles_many = [
            AutonomousCycleResult(
                cycle_id=i,
                objective=OptimizationObjective.GROWTH,
                previous_evolution_score=0.6 + i*0.02,
                new_evolution_score=0.65 + i*0.02,
                evolution_score_change=0.05,
                cycle_summary="Test",
                executive_decision=None,
            )
            for i in range(10)
        ]
        
        learning_many = update_intent_from_executive_decisions(
            CorporateIntent(),
            cycles_many
        )
        
        # 多数サイクルの方が信頼度が高い
        assert learning_many.learning_confidence >= learning_few.learning_confidence


if __name__ == "__main__":
    pytest.main([__file__, "-v"])