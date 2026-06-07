from typing import List
from ..models.strategy_model import (
    StrategyItem,
    StrategyHorizon,
    StrategyRiskLevel,
    StrategyRoadmap,
)
from ..models.self_optimization_model import (
    OptimizationObjective,
    SelfOptimizationPlan,
)
from ..models.corporate_story_model import CorporateStory


def determine_key_focus(plan: SelfOptimizationPlan) -> str:
    """Determine primary strategic focus from optimization objective"""
    focus_map = {
        OptimizationObjective.GROWTH: "成長ドライバーの最大化と新規市場開拓",
        OptimizationObjective.STABILITY: "収益とキャッシュフローの安定化",
        OptimizationObjective.INNOVATION: "新規事業・技術投資と組織革新",
        OptimizationObjective.PROFITABILITY: "利益率改善とコスト構造の最適化",
    }
    return focus_map.get(plan.objective, "戦略的フォーカスエリアの確定")


def _estimate_risk_level(impact: float, uncertainty: float) -> StrategyRiskLevel:
    """Estimate risk level based on impact and uncertainty"""
    # High impact + high uncertainty = HIGH risk
    # Low impact + low uncertainty = LOW risk
    combined_score = impact * 0.6 + uncertainty * 0.4
    
    if combined_score >= 0.7:
        return StrategyRiskLevel.HIGH
    elif combined_score >= 0.4:
        return StrategyRiskLevel.MEDIUM
    else:
        return StrategyRiskLevel.LOW


def _assign_horizon(strategy_title: str, impact: float) -> StrategyHorizon:
    """Assign execution horizon based on strategy type and impact"""
    # Strategy titles in Japanese - map to horizons
    short_term_keywords = ["コスト", "効率", "組織", "調整", "改善"]
    mid_term_keywords = ["新規", "投資", "協業", "展開", "強化"]
    long_term_keywords = ["文化", "構造", "変革", "進化", "根本"]
    
    title_lower = strategy_title.lower()
    
    for keyword in long_term_keywords:
        if keyword in strategy_title:
            return StrategyHorizon.LONG_TERM
    
    for keyword in mid_term_keywords:
        if keyword in strategy_title:
            return StrategyHorizon.MID_TERM
    
    for keyword in short_term_keywords:
        if keyword in strategy_title:
            return StrategyHorizon.SHORT_TERM
    
    # Default based on impact
    if impact >= 0.7:
        return StrategyHorizon.MID_TERM
    else:
        return StrategyHorizon.SHORT_TERM


def _build_strategy_dependencies(
    strategy_title: str,
    all_strategies: List[str]
) -> List[str]:
    """Build dependency list for a strategy"""
    dependencies = []
    
    # Culture shift dependencies
    if "新規" in strategy_title or "投資" in strategy_title:
        for strategy in all_strategies:
            if "文化" in strategy or "革新" in strategy:
                dependencies.append(strategy)
    
    # Structural dependencies
    if "構造" in strategy_title or "根本" in strategy_title:
        for strategy in all_strategies:
            if "組織" in strategy:
                dependencies.append(strategy)
    
    return list(set(dependencies))  # Remove duplicates


def build_strategy_items(
    plan: SelfOptimizationPlan,
    story: CorporateStory
) -> List[StrategyItem]:
    """Build strategy items from optimization plan"""
    items = []
    
    # Convert recommended strategies to StrategyItems
    for strategy in plan.recommended_strategies:
        # Extract priority and impact from the strategy object
        priority = getattr(strategy, "priority", 5)
        expected_impact = getattr(strategy, "expected_impact", 0.6)
        
        # Estimate uncertainty based on scenario and impact
        uncertainty = 0.3 if expected_impact >= 0.7 else 0.5
        
        # Create strategy item
        item = StrategyItem(
            title=strategy.strategy_name if hasattr(strategy, "strategy_name") else str(strategy),
            description=getattr(strategy, "description", "戦略的取り組み"),
            horizon=_assign_horizon(
                strategy.strategy_name if hasattr(strategy, "strategy_name") else str(strategy),
                expected_impact
            ),
            priority=priority,
            expected_impact=expected_impact,
            risk_level=_estimate_risk_level(expected_impact, uncertainty),
            dependencies=[]
        )
        items.append(item)
    
    # Add culture-related strategies if culture shifts recommended
    for culture_shift in plan.recommended_culture_shifts:
        title = f"文化シフト: {getattr(culture_shift, 'culture_type', '組織文化')}"
        item = StrategyItem(
            title=title,
            description=f"{getattr(culture_shift, 'culture_type', '文化')}を{getattr(culture_shift, 'shift_direction', '改善')}",
            horizon=StrategyHorizon.LONG_TERM,
            priority=3,
            expected_impact=0.6,
            risk_level=StrategyRiskLevel.MEDIUM,
            dependencies=[]
        )
        items.append(item)
    
    # Add leadership-related strategies if leadership changes recommended
    for leadership_change in plan.recommended_leadership_changes:
        title = f"リーダーシップ調整: {getattr(leadership_change, 'role', 'リーダー')}"
        item = StrategyItem(
            title=title,
            description=getattr(leadership_change, "description", "リーダーシップの強化"),
            horizon=StrategyHorizon.SHORT_TERM,
            priority=1,
            expected_impact=0.7,
            risk_level=StrategyRiskLevel.LOW,
            dependencies=[]
        )
        items.append(item)
    
    # Build dependencies
    all_titles = [item.title for item in items]
    for item in items:
        item.dependencies = _build_strategy_dependencies(item.title, all_titles)
    
    return items


def build_strategy_roadmap(
    plan: SelfOptimizationPlan,
    story: CorporateStory
) -> StrategyRoadmap:
    """Build complete strategy roadmap"""
    # Determine focus
    key_focus = determine_key_focus(plan)
    
    # Build strategy items
    strategies = build_strategy_items(plan, story)
    
    # Sort by priority
    strategies = sorted(strategies, key=lambda s: (s.priority, -s.expected_impact))
    
    # Create roadmap
    roadmap = StrategyRoadmap(
        objective=plan.objective,
        selected_scenario=plan.selected_scenario,
        key_focus=key_focus,
        strategies=strategies,
        notes=f"企業のストーリー: {story.summary}",
    )
    
    return roadmap
