from typing import List, Tuple, Dict, Optional
from statistics import mean, stdev
from uuid import uuid4

from ..models.corporate_intent_model import (
    CorporateIntent,
    IntentScore,
    IntentAlignment,
    IntentLearningHistory,
)
from ..models.multi_objective_model import ObjectiveVector, StrategyCandidate, ParetoFrontier
from ..models.autonomous_model import AutonomousCycleResult


def score_candidate(
    intent: CorporateIntent,
    candidate: StrategyCandidate,
) -> IntentScore:
    """
    Intent に基づいて Pareto frontier 上の候補をスコアリング

    重み付けスコアを計算し、リスク選好と時間軸で調整
    """
    vector = candidate.objective_vector

    # 基本スコア：Intent の重みと目的ベクトルの内積
    growth_component = intent.growth_weight * vector.growth
    profitability_component = intent.profitability_weight * vector.profitability
    innovation_component = intent.innovation_weight * vector.innovation
    stability_component = intent.stability_weight * vector.stability

    base_score = (
        growth_component
        + profitability_component
        + innovation_component
        + stability_component
    )

    # リスク選好による調整
    # risk = 1 - stability なので、リスク許容度が高いと高リスク・高収益を好む
    risk_level = 1.0 - vector.stability
    risk_adjustment = 1.0
    if intent.risk_preference > 0.5:
        # 攻め志向：リスク取得をボーナスに
        risk_bonus = intent.risk_preference * risk_level * 0.15
        risk_adjustment = 1.0 + risk_bonus
    else:
        # 保守志向：リスク回避をボーナスに
        risk_aversion = (1.0 - intent.risk_preference) * vector.stability * 0.15
        risk_adjustment = 1.0 + risk_aversion

    # 時間軸による調整
    # 長期志向なら innovation と stability を強める
    time_horizon_adjustment = 1.0
    if intent.time_horizon > 0.5:
        # 長期志向：革新と安定のバランスが重要
        innovation_bonus = intent.time_horizon * vector.innovation * 0.1
        stability_bonus = (1.0 - intent.time_horizon * 0.3) * vector.stability * 0.05
        time_horizon_adjustment = 1.0 + innovation_bonus + stability_bonus
    else:
        # 短期志向：成長と収益性を強める
        short_term_boost = (1.0 - intent.time_horizon) * (vector.growth + vector.profitability) * 0.05
        time_horizon_adjustment = 1.0 + short_term_boost

    # 最終スコア
    final_score = base_score * risk_adjustment * time_horizon_adjustment

    return IntentScore(
        candidate_id=f"{candidate.scenario_type}_{candidate.optimization_objective}",
        candidate_desc=f"{candidate.scenario_type} / {candidate.optimization_objective}",
        score=final_score,
        growth_component=growth_component,
        profitability_component=profitability_component,
        innovation_component=innovation_component,
        stability_component=stability_component,
        risk_adjustment=risk_adjustment,
        time_horizon_adjustment=time_horizon_adjustment,
        breakdown={
            "growth": growth_component,
            "profitability": profitability_component,
            "innovation": innovation_component,
            "stability": stability_component,
            "base_score": base_score,
            "final_score": final_score,
        },
    )


def select_strategy_by_intent(
    intent: CorporateIntent, frontier: ParetoFrontier
) -> Tuple[StrategyCandidate, IntentScore]:
    """
    Intent に基づいて Pareto frontier から最適戦略を選択

    Returns:
        (最適候補, スコア) のタプル
    """
    scored_candidates = [
        (candidate, score_candidate(intent, candidate)) for candidate in frontier.candidates
    ]

    best_candidate, best_score = max(scored_candidates, key=lambda x: x[1].score)
    return best_candidate, best_score


def rank_candidates_by_intent(
    intent: CorporateIntent, frontier: ParetoFrontier
) -> List[Tuple[StrategyCandidate, IntentScore]]:
    """
    Pareto frontier 上のすべての候補を Intent スコアでランク付け

    Returns:
        スコア降順の (候補, スコア) リスト
    """
    scored = [
        (candidate, score_candidate(intent, candidate)) for candidate in frontier.candidates
    ]
    return sorted(scored, key=lambda x: x[1].score, reverse=True)


def calculate_intent_alignment(
    intent: CorporateIntent, candidate: StrategyCandidate
) -> IntentAlignment:
    """
    戦略の企業 Intent への整合性を評価

    整合性スコア（0-1）と整合/非整合の目的を返す
    """
    vector = candidate.objective_vector

    # 各目的の寄与度を計算
    growth_contribution = intent.growth_weight * (vector.growth / 150.0)  # 正規化
    profit_contribution = intent.profitability_weight * (vector.profitability / 20.0)
    innovation_contribution = intent.innovation_weight * vector.innovation
    stability_contribution = intent.stability_weight * vector.stability

    # スコアが高い（>平均）なら整合、低い（<平均）なら非整合
    avg_contribution = (
        growth_contribution
        + profit_contribution
        + innovation_contribution
        + stability_contribution
    ) / 4.0

    aligned = []
    misaligned = []

    if growth_contribution > avg_contribution:
        aligned.append("growth")
    else:
        misaligned.append("growth")

    if profit_contribution > avg_contribution:
        aligned.append("profitability")
    else:
        misaligned.append("profitability")

    if innovation_contribution > avg_contribution:
        aligned.append("innovation")
    else:
        misaligned.append("innovation")

    if stability_contribution > avg_contribution:
        aligned.append("stability")
    else:
        misaligned.append("stability")

    alignment_score = max(0.0, min(1.0, growth_contribution + profit_contribution + innovation_contribution + stability_contribution))

    explanation = f"Strategy aligns with {', '.join(aligned)} priorities and conflicts with {', '.join(misaligned)}"

    return IntentAlignment(
        strategy_id=f"{candidate.scenario_type}_{candidate.optimization_objective}",
        strategy_desc=candidate.roadmap_title,
        intent_alignment_score=alignment_score,
        aligned_objectives=aligned,
        misaligned_objectives=misaligned,
        explanation=explanation,
    )


def update_intent_from_history(
    intent: CorporateIntent, history: List[AutonomousCycleResult]
) -> IntentLearningHistory:
    """
    企業が過去に選んだ戦略から企業意思を学習・推定

    過去のサイクルで選ばれた戦略の特性から、
    企業が実際に何を優先しているかを逆推定
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
        )

    # 過去のサイクルから統計を取得
    growth_values = []
    profitability_values = []
    innovation_values = []
    stability_values = []
    risk_values = []

    objective_dist = {}

    for cycle in history:
        # 各戦略の目的ベクトルを収集
        # Note: autonomous_model では applied_strategies が保存されている
        if hasattr(cycle, "objective") and cycle.objective:
            obj_name = cycle.objective.value
            objective_dist[obj_name] = objective_dist.get(obj_name, 0) + 1

    # 統計情報から Average と Volatility を計算
    if history:
        # evolution_score_change から innovation 傾向を推定
        innovation_values = [c.evolution_score_change for c in history]
        avg_innovation = mean(innovation_values) if innovation_values else 0.0

        # autonomousの結果から成長志向を推定
        # 新規戦略数が多い = 成長志向
        avg_growth = len([c for c in history if "新規" in str(getattr(c, "strategy_applications", {}))]) / len(history) * 100 if history else 0.0

        # リスク取得傾向
        avg_risk_taken = mean([0.5] * len(history)) if history else 0.0
        risk_volatility = stdev([0.5] * len(history)) if len(history) > 1 else 0.0

    else:
        avg_innovation = 0.0
        avg_growth = 0.0
        avg_risk_taken = 0.0
        risk_volatility = 0.0

    avg_profitability = 0.0  # Will be inferred from context
    avg_stability = 1.0 - avg_risk_taken

    # 学習から推定される Intent を生成
    total = max(1.0, avg_growth + avg_profitability + avg_innovation + avg_stability)
    inferred_growth_weight = avg_growth / total if total > 0 else 0.25
    inferred_profit_weight = avg_profitability / total if total > 0 else 0.25
    inferred_innovation_weight = avg_innovation / total if total > 0 else 0.25
    inferred_stability_weight = avg_stability / total if total > 0 else 0.25

    # 学習に基づいて Intent を更新（現在の Intent と 30% ブレンド）
    updated_intent = CorporateIntent(
        growth_weight=intent.growth_weight * 0.7 + inferred_growth_weight * 0.3,
        profitability_weight=intent.profitability_weight * 0.7 + inferred_profit_weight * 0.3,
        innovation_weight=intent.innovation_weight * 0.7 + inferred_innovation_weight * 0.3,
        stability_weight=intent.stability_weight * 0.7 + inferred_stability_weight * 0.3,
        risk_preference=max(0.0, min(1.0, intent.risk_preference * 0.7 + avg_risk_taken * 0.3)),
        time_horizon=intent.time_horizon,
        cultural_identity=intent.cultural_identity,
    )
    updated_intent.normalize_weights()

    # 学習信頼度（データ点数が多いほど高い）
    learning_confidence = min(1.0, len(history) / 10.0)

    return IntentLearningHistory(
        cycle_count=len(history),
        avg_growth=avg_growth,
        avg_profitability=avg_profitability,
        avg_innovation=avg_innovation,
        avg_stability=avg_stability,
        avg_risk_taken=avg_risk_taken,
        risk_volatility=risk_volatility,
        objective_distribution=objective_dist,
        inferred_intent=updated_intent,
        learning_confidence=learning_confidence,
    )


def apply_learning_to_intent(
    current_intent: CorporateIntent, learning_history: IntentLearningHistory
) -> CorporateIntent:
    """
    学習結果を現在の Intent に適用

    学習信頼度に基づいて段階的に Intent を更新
    """
    if not learning_history.inferred_intent:
        return current_intent

    inferred = learning_history.inferred_intent
    confidence = learning_history.learning_confidence

    # 信頼度に基づいてブレンド
    updated_intent = CorporateIntent(
        growth_weight=current_intent.growth_weight * (1 - confidence) + inferred.growth_weight * confidence,
        profitability_weight=current_intent.profitability_weight * (1 - confidence) + inferred.profitability_weight * confidence,
        innovation_weight=current_intent.innovation_weight * (1 - confidence) + inferred.innovation_weight * confidence,
        stability_weight=current_intent.stability_weight * (1 - confidence) + inferred.stability_weight * confidence,
        risk_preference=current_intent.risk_preference * (1 - confidence) + inferred.risk_preference * confidence,
        time_horizon=current_intent.time_horizon,
        cultural_identity=current_intent.cultural_identity,
    )
    updated_intent.normalize_weights()

    return updated_intent
