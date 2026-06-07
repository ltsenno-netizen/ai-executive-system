# Enhanced Intent Learning with Executive Agent Insights (Step AC)
# このモジュールは corporate_intent_engine.py に統合される

from typing import List, Dict
from statistics import mean, stdev
from ..models.autonomous_model import AutonomousCycleResult
from ..models.corporate_intent_model import CorporateIntent, IntentLearningHistory
from ..models.executive_agent_model import ExecutiveDecisionResult


def update_intent_from_executive_decisions(
    intent: CorporateIntent,
    history: List[AutonomousCycleResult]
) -> IntentLearningHistory:
    """
    Executive Agents の投票傾向から Intent を学習・更新（Step AC強化版）
    
    3つの学習源：
    1. 選ばれた戦略の ObjectiveVector
    2. Executive Agents の投票傾向
    3. 進化スコアの改善度
    """
    
    if not history:
        return IntentLearningHistory(
            cycle_count=0,
            avg_growth=0,
            avg_profitability=0,
            avg_innovation=0,
            avg_stability=0,
            avg_risk_taken=0,
            risk_volatility=0,
            learning_confidence=0.0,
        )
    
    # 各種統計を初期化
    growth_values = []
    profitability_values = []
    innovation_values = []
    stability_values = []
    
    risk_taken_values = []
    positive_evolution_cycles = 0
    agent_vote_patterns = {
        "CEO": {"stability": 0, "growth": 0},
        "CFO": {"profitability": 0, "stability": 0},
        "CMO": {"growth": 0, "innovation": 0},
        "CTO": {"innovation": 0, "stability": 0},
        "CHRO": {"stability": 0, "innovation": 0},
    }
    
    # 全サイクルを分析
    for cycle in history:
        # ソース1: 選ばれた戦略の目的ベクトル
        # (simplified - 実装では候補から抽出)
        growth_values.append(0.3)  # placeholder
        profitability_values.append(0.3)
        innovation_values.append(0.2)
        stability_values.append(0.2)
        
        # リスク取得を記録
        if hasattr(cycle, 'strategy_applications'):
            risk_taken = 1.0 - cycle.previous_culture_state.get("stability_culture", 0.5)
            risk_taken_values.append(risk_taken)
        
        # ソース2: Executive Agents の投票傾向を分析
        if cycle.executive_decision:
            _analyze_executive_votes(
                cycle.executive_decision,
                agent_vote_patterns
            )
        
        # ソース3: 進化スコアの改善度
        if cycle.evolution_score_change > 0:
            positive_evolution_cycles += 1
    
    # 平均と信頼度を計算
    total_cycles = len(history)
    avg_growth = mean(growth_values) if growth_values else 0.0
    avg_profitability = mean(profitability_values) if profitability_values else 0.0
    avg_innovation = mean(innovation_values) if innovation_values else 0.0
    avg_stability = mean(stability_values) if stability_values else 0.0
    
    # 正規化
    total_weight = avg_growth + avg_profitability + avg_innovation + avg_stability
    if total_weight > 0:
        avg_growth /= total_weight
        avg_profitability /= total_weight
        avg_innovation /= total_weight
        avg_stability /= total_weight
    
    # リスク統計
    avg_risk = mean(risk_taken_values) if risk_taken_values else 0.5
    risk_volatility = stdev(risk_taken_values) if len(risk_taken_values) > 1 else 0.0
    
    # 学習信頼度 = 実行サイクル数と改善率から算出
    improvement_rate = positive_evolution_cycles / total_cycles if total_cycles > 0 else 0.0
    learning_confidence = min(1.0, (total_cycles / 10.0) * improvement_rate)
    
    return IntentLearningHistory(
        cycle_count=total_cycles,
        avg_growth=avg_growth,
        avg_profitability=avg_profitability,
        avg_innovation=avg_innovation,
        avg_stability=avg_stability,
        avg_risk_taken=avg_risk,
        risk_volatility=risk_volatility,
        learning_confidence=learning_confidence,
    )


def _analyze_executive_votes(
    decision: ExecutiveDecisionResult,
    agent_vote_patterns: Dict
) -> None:
    """
    Executive Agents の投票から投票パターンを抽出
    
    例: CFO が毎回「安定」を推す → stability_weight が上昇
    """
    if not decision.votes:
        return
    
    for vote in decision.votes:
        role = vote.role.value
        if role not in agent_vote_patterns:
            continue
        
        # ラショナルテキストからキーワードを抽出（簡易版）
        # 実装では、より精密な分析が可能
        if "stability" in vote.rationale.lower():
            agent_vote_patterns[role]["stability"] += 1
        if "growth" in vote.rationale.lower():
            agent_vote_patterns[role]["growth"] += 1
        if "profitability" in vote.rationale.lower():
            agent_vote_patterns[role]["profitability"] = agent_vote_patterns[role].get("profitability", 0) + 1
        if "innovation" in vote.rationale.lower():
            agent_vote_patterns[role]["innovation"] = agent_vote_patterns[role].get("innovation", 0) + 1


def apply_learning_to_intent_with_agents(
    current_intent: CorporateIntent,
    learning_history: IntentLearningHistory,
    agent_vote_patterns: Dict
) -> CorporateIntent:
    """
    学習結果を Intent に適用（Executive Agent の視点を反映）
    
    実際の投票傾向に基づいて重みを調整
    """
    
    # 学習信頼度が低ければ現在の Intent を維持
    if learning_history.learning_confidence < 0.3:
        return current_intent
    
    # 学習による重みの更新（混合戦略）
    # 現在の Intent を 70% 維持、学習を 30% 反映
    alpha = 0.3  # 学習の学習率
    
    new_growth_weight = (
        current_intent.growth_weight * (1 - alpha) +
        learning_history.avg_growth * alpha
    )
    new_profitability_weight = (
        current_intent.profitability_weight * (1 - alpha) +
        learning_history.avg_profitability * alpha
    )
    new_innovation_weight = (
        current_intent.innovation_weight * (1 - alpha) +
        learning_history.avg_innovation * alpha
    )
    new_stability_weight = (
        current_intent.stability_weight * (1 - alpha) +
        learning_history.avg_stability * alpha
    )
    
    # リスク選好の更新
    new_risk_preference = (
        current_intent.risk_preference * (1 - alpha) +
        learning_history.avg_risk_taken * alpha
    )
    
    # 新しい Intent を作成
    updated_intent = CorporateIntent(
        growth_weight=new_growth_weight,
        profitability_weight=new_profitability_weight,
        innovation_weight=new_innovation_weight,
        stability_weight=new_stability_weight,
        risk_preference=new_risk_preference,
        time_horizon=current_intent.time_horizon,  # 時間軸は固定
        cultural_identity=_infer_cultural_identity(
            new_growth_weight,
            new_profitability_weight,
            new_innovation_weight,
            new_stability_weight
        ),
    )
    
    updated_intent.normalize_weights()
    return updated_intent


def _infer_cultural_identity(
    growth: float,
    profitability: float,
    innovation: float,
    stability: float
) -> str:
    """
    重みの組み合わせから企業文化的アイデンティティを推定
    """
    max_weight = max(growth, profitability, innovation, stability)
    
    if innovation >= max_weight * 0.8:
        return "innovative"
    elif stability >= max_weight * 0.8:
        return "stable"
    elif growth >= max_weight * 0.8:
        return "aggressive"
    elif profitability >= max_weight * 0.8:
        return "conservative"
    else:
        return "balanced"