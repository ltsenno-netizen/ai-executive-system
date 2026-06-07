from typing import Dict, Tuple
from ..models.strategy_model import StrategyRoadmap, StrategyItem
from ..models.culture_model import CultureProfile
from ..models.ai_ceo_model import AICeoPersona
from ..models.external_environment_model_v2 import ExternalEnvironmentState
from ..models.enterprise_evolution_model import EnterpriseEvolutionResult


def _extract_keywords(text: str) -> list:
    """Extract Japanese keywords from strategy text"""
    keywords = [
        "新規事業", "投資", "R&D", "技術", "innovation",
        "文化", "culture", "シフト",
        "CFO", "CEO", "CMO", "COO", "CTO",
        "コスト", "効率", "cost", "efficiency",
        "ブランド", "マーケティング", "営業",
        "組織", "改編", "リーダーシップ",
        "M&A", "買収", "協業", "partnership"
    ]
    text_lower = text.lower()
    found = []
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found.append(keyword)
    return found


def _apply_strategy_to_culture(
    strategy: StrategyItem,
    culture: CultureProfile
) -> CultureProfile:
    """Apply strategy to culture profile"""
    keywords = _extract_keywords(strategy.title + " " + strategy.description)
    impact_multiplier = strategy.expected_impact
    
    # Make a copy
    new_culture = CultureProfile(**culture.model_dump())
    
    # Innovation-related strategies
    if any(k in keywords for k in ["新規事業", "innovation", "R&D", "技術"]):
        new_culture.innovation_culture = min(1.0, new_culture.innovation_culture + (0.05 * impact_multiplier))
        new_culture.aggressiveness_culture = min(1.0, new_culture.aggressiveness_culture + (0.03 * impact_multiplier))
    
    # Cost-related strategies
    if any(k in keywords for k in ["コスト", "効率", "cost"]):
        new_culture.cost_culture = min(1.0, new_culture.cost_culture + (0.08 * impact_multiplier))
        new_culture.execution_culture = min(1.0, new_culture.execution_culture + (0.04 * impact_multiplier))
    
    # Brand/Marketing strategies
    if any(k in keywords for k in ["ブランド", "マーケティング"]):
        new_culture.brand_culture = min(1.0, new_culture.brand_culture + (0.06 * impact_multiplier))
        new_culture.market_culture = min(1.0, new_culture.market_culture + (0.05 * impact_multiplier))
    
    # Stability-focused strategies
    if any(k in keywords for k in ["安定", "stability"]):
        new_culture.stability_culture = min(1.0, new_culture.stability_culture + (0.07 * impact_multiplier))
        new_culture.risk_aversion_culture = min(1.0, new_culture.risk_aversion_culture + (0.04 * impact_multiplier))
    
    # Organization/Process strategies
    if any(k in keywords for k in ["組織", "改編", "process"]):
        new_culture.process_culture = min(1.0, new_culture.process_culture + (0.06 * impact_multiplier))
        new_culture.execution_culture = min(1.0, new_culture.execution_culture + (0.03 * impact_multiplier))
    
    # People/Talent strategies
    if "人事" in strategy.title or "人材" in strategy.title:
        new_culture.people_culture = min(1.0, new_culture.people_culture + (0.07 * impact_multiplier))
    
    return new_culture


def _apply_strategy_to_executive_team(
    strategy: StrategyItem,
    executive_team: Dict[str, AICeoPersona]
) -> Dict[str, AICeoPersona]:
    """Apply strategy to executive team personas"""
    keywords = _extract_keywords(strategy.title + " " + strategy.description)
    impact_multiplier = strategy.expected_impact
    
    # Make a copy
    new_team = {}
    for role, persona in executive_team.items():
        new_team[role] = AICeoPersona(
            aggressiveness=persona.aggressiveness,
            risk_tolerance=persona.risk_tolerance,
            brand_priority=persona.brand_priority,
            short_term_focus=persona.short_term_focus,
            long_term_focus=persona.long_term_focus
        )
    
    # CEO adjustments
    if any(k in keywords for k in ["新規事業", "投資", "innovation"]):
        if "CEO" in new_team:
            new_team["CEO"].aggressiveness = min(1.0, new_team["CEO"].aggressiveness + (0.05 * impact_multiplier))
            new_team["CEO"].long_term_focus = min(1.0, new_team["CEO"].long_term_focus + (0.03 * impact_multiplier))
    
    # CFO adjustments
    if any(k in keywords for k in ["コスト", "効率", "CFO", "財務"]):
        if "CFO" in new_team:
            new_team["CFO"].risk_tolerance = max(0.0, new_team["CFO"].risk_tolerance - (0.03 * impact_multiplier))
    
    # CMO adjustments
    if any(k in keywords for k in ["ブランド", "マーケティング", "CMO", "営業"]):
        if "CMO" in new_team:
            new_team["CMO"].aggressiveness = min(1.0, new_team["CMO"].aggressiveness + (0.05 * impact_multiplier))
            new_team["CMO"].brand_priority = min(1.0, new_team["CMO"].brand_priority + (0.06 * impact_multiplier))
    
    # CTO adjustments
    if any(k in keywords for k in ["R&D", "技術", "CTO", "innovation"]):
        if "CTO" in new_team:
            new_team["CTO"].long_term_focus = min(1.0, new_team["CTO"].long_term_focus + (0.06 * impact_multiplier))
    
    return new_team


def _apply_strategy_to_evolution(
    strategy: StrategyItem,
    evolution: EnterpriseEvolutionResult
) -> EnterpriseEvolutionResult:
    """Apply strategy to evolution score"""
    keywords = _extract_keywords(strategy.title + " " + strategy.description)
    impact_multiplier = strategy.expected_impact
    base_impact = 0.08  # Base evolution score change
    
    # Determine strategy category impact
    if any(k in keywords for k in ["新規事業", "投資", "M&A", "innovation", "R&D"]):
        evolution_change = base_impact * impact_multiplier * 1.5  # High impact for innovation
    elif any(k in keywords for k in ["文化", "culture", "リーダーシップ"]):
        evolution_change = base_impact * impact_multiplier * 1.2  # Moderate impact for culture
    elif any(k in keywords for k in ["コスト", "効率", "営業"]):
        evolution_change = base_impact * impact_multiplier * 0.8  # Moderate impact for operations
    else:
        evolution_change = base_impact * impact_multiplier * 0.5  # Low impact for others
    
    new_evolution_score = min(1.0, evolution.evolution_score + evolution_change)
    
    # Create new evolution result
    new_evolution = EnterpriseEvolutionResult(
        evolution_score=new_evolution_score,
        environment_pressure=evolution.environment_pressure,
        culture_shift=evolution.culture_shift,
        leadership_shift=evolution.leadership_shift
    )
    
    return new_evolution


def apply_strategy_roadmap_to_state(
    roadmap: StrategyRoadmap,
    culture: CultureProfile,
    executive_team: Dict[str, AICeoPersona],
    environment: ExternalEnvironmentState,
    evolution: EnterpriseEvolutionResult,
) -> Tuple[CultureProfile, Dict[str, AICeoPersona], ExternalEnvironmentState, EnterpriseEvolutionResult, Dict]:
    """
    Apply all strategies from roadmap to internal state.
    
    Returns:
        Tuple of (new_culture, new_executive_team, new_environment, new_evolution, application_details)
    """
    new_culture = culture
    new_executive_team = executive_team
    new_environment = environment  # Environment generally doesn't change from strategy application
    new_evolution = evolution
    
    application_details = {}
    
    # Apply strategies in priority order
    for strategy in sorted(roadmap.strategies, key=lambda s: s.priority):
        # Apply to culture
        new_culture = _apply_strategy_to_culture(strategy, new_culture)
        
        # Apply to executive team
        new_executive_team = _apply_strategy_to_executive_team(strategy, new_executive_team)
        
        # Apply to evolution score
        new_evolution = _apply_strategy_to_evolution(strategy, new_evolution)
        
        # Track application details
        application_details[strategy.title] = {
            "priority": strategy.priority,
            "expected_impact": strategy.expected_impact,
            "risk_level": strategy.risk_level.value,
            "horizon": strategy.horizon.value,
            "applied": True
        }
    
    return new_culture, new_executive_team, new_environment, new_evolution, application_details


def calculate_strategy_effectiveness(
    previous_evolution: float,
    new_evolution: float,
    strategy_count: int
) -> float:
    """Calculate effectiveness of strategy application (impact per strategy)"""
    if strategy_count == 0:
        return 0.0
    return (new_evolution - previous_evolution) / strategy_count
