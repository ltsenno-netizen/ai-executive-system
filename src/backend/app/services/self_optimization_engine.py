from typing import List, Dict
from ..models.self_optimization_model import (
    OptimizationObjective,
    StrategyAdjustment,
    CultureAdjustment,
    LeadershipAdjustment,
    SelfOptimizationPlan
)
from ..models.scenario_model import ScenarioResult, ScenarioType
from ..models.culture_model import CultureProfile
from ..models.ai_ceo_model import AICeoPersona


def select_best_scenario(
    objective: OptimizationObjective,
    scenario_results: List[ScenarioResult]
) -> ScenarioResult:
    """
    目的に応じて最適シナリオを選ぶ:
    - GROWTH: projected_revenue 最大
    - STABILITY: risk_level が低く、evolution_score が安定
    - INNOVATION: projected_evolution_score 最大
    - PROFITABILITY: projected_profit 最大
    """
    if objective == OptimizationObjective.GROWTH:
        return max(scenario_results, key=lambda r: r.projected_financials.get("revenue", 0))
    elif objective == OptimizationObjective.STABILITY:
        # リスクが低く、進化スコアが安定したものを選ぶ
        return min(scenario_results, key=lambda r: (r.risk_assessment == "High", -r.projected_evolution_score))
    elif objective == OptimizationObjective.INNOVATION:
        return max(scenario_results, key=lambda r: r.projected_evolution_score)
    elif objective == OptimizationObjective.PROFITABILITY:
        return max(scenario_results, key=lambda r: r.projected_financials.get("profit", 0))
    else:
        return scenario_results[0]  # fallback


def build_strategy_adjustments(
    scenario: ScenarioResult,
    current_financials: Dict[str, float]
) -> List[StrategyAdjustment]:
    """
    例:
    - revenue が低い → 「新規事業投資」「マーケ強化」
    - profit が低い → 「コスト構造見直し」
    - evolution_score が低い → 「イノベーション投資」
    """
    adjustments = []
    revenue = scenario.projected_financials.get("revenue", 0)
    profit = scenario.projected_financials.get("profit", 0)
    evolution_score = scenario.projected_evolution_score

    if revenue < current_financials.get("revenue", 0) * 1.1:  # 10%未満成長
        adjustments.append(StrategyAdjustment(
            description="新規事業投資を強化",
            priority=1,
            expected_impact=0.8
        ))
        adjustments.append(StrategyAdjustment(
            description="マーケティング予算を増大",
            priority=2,
            expected_impact=0.6
        ))

    if profit < current_financials.get("profit", 0) * 1.05:  # 5%未満成長
        adjustments.append(StrategyAdjustment(
            description="コスト構造の見直し",
            priority=1,
            expected_impact=0.7
        ))

    if evolution_score < 0.6:
        adjustments.append(StrategyAdjustment(
            description="イノベーション投資を増加",
            priority=2,
            expected_impact=0.9
        ))

    return adjustments


def build_culture_adjustments(
    scenario: ScenarioResult,
    current_culture: CultureProfile
) -> List[CultureAdjustment]:
    """
    例:
    - tech boom シナリオ → innovation_culture を +0.1 推奨
    - recession シナリオ → stability_culture を +0.1 推奨
    """
    adjustments = []

    if scenario.scenario_type == ScenarioType.TECH_BOOM:
        adjustments.append(CultureAdjustment(
            dimension="innovation_culture",
            delta=0.1,
            rationale="技術革新期にはイノベーション文化を強化"
        ))
    elif scenario.scenario_type == ScenarioType.RECESSION:
        adjustments.append(CultureAdjustment(
            dimension="stability_culture",
            delta=0.1,
            rationale="不況期には安定性を重視"
        ))
    elif scenario.scenario_type == ScenarioType.OPTIMISTIC:
        adjustments.append(CultureAdjustment(
            dimension="aggressiveness_culture",
            delta=0.05,
            rationale="好況期には積極性を高める"
        ))

    return adjustments


def build_leadership_adjustments(
    scenario: ScenarioResult,
    current_executive_team: Dict[str, AICeoPersona]
) -> List[LeadershipAdjustment]:
    """
    例:
    - risk が高いのに CFO が攻め型 → CFO を「develop」 or 「replace」推奨
    - tech boom なのに CMO の innovation_bias が低い → CMO を「develop」推奨
    """
    adjustments = []

    if scenario.scenario_type == ScenarioType.RECESSION:
        if "CFO" in current_executive_team:
            cfo = current_executive_team["CFO"]
            if cfo.risk_tolerance > 0.7:  # リスク許容度が高い
                adjustments.append(LeadershipAdjustment(
                    role="CFO",
                    suggested_change="develop",
                    rationale="不況期にはリスク管理を強化"
                ))

    if scenario.scenario_type == ScenarioType.TECH_BOOM:
        if "CMO" in current_executive_team:
            cmo = current_executive_team["CMO"]
            # 仮定: innovation_bias が低い場合
            if getattr(cmo, "innovation_bias", 0.5) < 0.6:
                adjustments.append(LeadershipAdjustment(
                    role="CMO",
                    suggested_change="develop",
                    rationale="技術革新期にはイノベーション能力を強化"
                ))

    # デフォルトでkeep
    for role in current_executive_team.keys():
        if not any(adj.role == role for adj in adjustments):
            adjustments.append(LeadershipAdjustment(
                role=role,
                suggested_change="keep",
                rationale="現在の構成を維持"
            ))

    return adjustments


def build_self_optimization_plan(
    objective: OptimizationObjective,
    scenario_results: List[ScenarioResult],
    current_culture: CultureProfile,
    current_executive_team: Dict[str, AICeoPersona],
    current_financials: Dict[str, float]
) -> SelfOptimizationPlan:
    best_scenario = select_best_scenario(objective, scenario_results)
    strategies = build_strategy_adjustments(best_scenario, current_financials)
    culture_shifts = build_culture_adjustments(best_scenario, current_culture)
    leadership_changes = build_leadership_adjustments(best_scenario, current_executive_team)

    return SelfOptimizationPlan(
        objective=objective,
        selected_scenario=best_scenario.scenario_type,
        recommended_strategies=strategies,
        recommended_culture_shifts=culture_shifts,
        recommended_leadership_changes=leadership_changes,
        expected_evolution_score=best_scenario.projected_evolution_score,
        notes="Self-optimization plan generated based on scenario planning results."
    )
