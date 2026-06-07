from typing import List, Tuple
from ..models.multi_objective_model import (
    ObjectiveVector,
    StrategyCandidate,
    ParetoFrontier,
    ParetoDominanceInfo,
)
from ..models.scenario_model import ScenarioResult
from ..models.self_optimization_model import SelfOptimizationPlan
from ..models.strategy_model import StrategyRoadmap


def normalize_value(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Normalize value to 0-1 range"""
    if max_val <= min_val:
        return 0.5
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def compute_objective_vector(
    scenario: ScenarioResult,
    plan: SelfOptimizationPlan,
) -> ObjectiveVector:
    """Compute objective vector from scenario and optimization plan"""
    
    # Extract growth (from projected revenue)
    growth = scenario.projected_financials.get("revenue", 100.0)
    
    # Extract profitability (from projected profit)
    profitability = scenario.projected_financials.get("profit", 10.0)
    
    # Innovation from evolution score
    innovation = scenario.projected_evolution_score
    
    # Stability: inverse of risk (0-1 scale)
    # Calculate risk score from risk_assessment text
    risk_text = scenario.risk_assessment.lower()
    if "high" in risk_text:
        risk_score = 0.7
    elif "medium" in risk_text:
        risk_score = 0.4
    else:
        risk_score = 0.2
    
    stability = 1.0 - risk_score
    
    return ObjectiveVector(
        growth=growth,
        profitability=profitability,
        innovation=innovation,
        stability=stability,
    )


def dominates(a: ObjectiveVector, b: ObjectiveVector) -> bool:
    """
    Check if objective vector 'a' dominates objective vector 'b'.
    
    A dominates B if:
    - A is >= B in all dimensions
    - A is > B in at least one dimension
    """
    at_least_as_good = (
        a.growth >= b.growth and
        a.profitability >= b.profitability and
        a.innovation >= b.innovation and
        a.stability >= b.stability
    )
    
    strictly_better = (
        a.growth > b.growth or
        a.profitability > b.profitability or
        a.innovation > b.innovation or
        a.stability > b.stability
    )
    
    return at_least_as_good and strictly_better


def build_pareto_frontier(candidates: List[StrategyCandidate]) -> ParetoFrontier:
    """
    Build Pareto frontier from strategy candidates.
    
    Returns only non-dominated candidates.
    """
    if not candidates:
        return ParetoFrontier(
            total_candidates=0,
            frontier_count=0,
            candidates=[],
            frontier_indices=[],
            best_growth=0.0,
            best_profitability=0.0,
            best_innovation=0.0,
            best_stability=0.0,
            summary="No candidates provided"
        )
    
    # Identify frontier candidates
    frontier_indices = []
    dominance_info_list = []
    
    for i, candidate_i in enumerate(candidates):
        dominated_by = []
        dominates_list = []
        is_frontier = True
        
        for j, candidate_j in enumerate(candidates):
            if i == j:
                continue
            
            if dominates(candidate_j.objective_vector, candidate_i.objective_vector):
                dominated_by.append(j)
                is_frontier = False
            elif dominates(candidate_i.objective_vector, candidate_j.objective_vector):
                dominates_list.append(j)
        
        if is_frontier:
            frontier_indices.append(i)
        
        dominance_info_list.append(
            ParetoDominanceInfo(
                candidate_index=i,
                dominated_by=dominated_by,
                dominates=dominates_list,
                is_pareto_optimal=is_frontier,
            )
        )
    
    # Get frontier candidates
    frontier_candidates = [candidates[i] for i in frontier_indices]
    
    # Calculate aggregate statistics
    best_growth = max((c.objective_vector.growth for c in frontier_candidates), default=0.0)
    best_profitability = max((c.objective_vector.profitability for c in frontier_candidates), default=0.0)
    best_innovation = max((c.objective_vector.innovation for c in frontier_candidates), default=0.0)
    best_stability = max((c.objective_vector.stability for c in frontier_candidates), default=0.0)
    
    summary = (
        f"{len(frontier_indices)} Pareto-optimal strategies identified from {len(candidates)} candidates. "
        f"Frontier trades off: Growth={best_growth:.1f}, Profit={best_profitability:.1f}, "
        f"Innovation={best_innovation:.2f}, Stability={best_stability:.2f}"
    )
    
    return ParetoFrontier(
        total_candidates=len(candidates),
        frontier_count=len(frontier_indices),
        candidates=candidates,
        frontier_indices=frontier_indices,
        dominance_info=dominance_info_list,
        best_growth=best_growth,
        best_profitability=best_profitability,
        best_innovation=best_innovation,
        best_stability=best_stability,
        summary=summary,
    )


def identify_tradeoffs(frontier: ParetoFrontier) -> dict:
    """
    Analyze tradeoffs in Pareto frontier.
    
    Returns information about conflicting objectives.
    """
    if frontier.frontier_count < 2:
        return {
            "growth_vs_profitability": 0.0,
            "growth_vs_stability": 0.0,
            "innovation_vs_profitability": 0.0,
            "innovation_vs_stability": 0.0,
            "description": "Insufficient frontier candidates for tradeoff analysis"
        }
    
    frontier_vectors = [
        frontier.candidates[i].objective_vector
        for i in frontier.frontier_indices
    ]
    
    # Calculate range ratios for each objective
    growth_range = frontier.best_growth - min(v.growth for v in frontier_vectors)
    profit_range = frontier.best_profitability - min(v.profitability for v in frontier_vectors)
    innovation_range = frontier.best_innovation - min(v.innovation for v in frontier_vectors)
    stability_range = frontier.best_stability - min(v.stability for v in frontier_vectors)
    
    # Calculate correlations (negative = tradeoff)
    growth_vs_profit = _calculate_correlation(frontier_vectors, lambda v: v.growth, lambda v: v.profitability)
    growth_vs_stability = _calculate_correlation(frontier_vectors, lambda v: v.growth, lambda v: v.stability)
    innovation_vs_profit = _calculate_correlation(frontier_vectors, lambda v: v.innovation, lambda v: v.profitability)
    innovation_vs_stability = _calculate_correlation(frontier_vectors, lambda v: v.innovation, lambda v: v.stability)
    
    return {
        "growth_vs_profitability": growth_vs_profit,
        "growth_vs_stability": growth_vs_stability,
        "innovation_vs_profitability": innovation_vs_profit,
        "innovation_vs_stability": innovation_vs_stability,
        "interpretation": _interpret_tradeoffs(
            growth_vs_profit,
            growth_vs_stability,
            innovation_vs_profit,
            innovation_vs_stability
        )
    }


def _calculate_correlation(vectors: list, x_func, y_func) -> float:
    """Calculate simple correlation between two objectives"""
    if len(vectors) < 2:
        return 0.0
    
    x_vals = [x_func(v) for v in vectors]
    y_vals = [y_func(v) for v in vectors]
    
    mean_x = sum(x_vals) / len(x_vals)
    mean_y = sum(y_vals) / len(y_vals)
    
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals)) / len(vectors)
    std_x = (sum((x - mean_x) ** 2 for x in x_vals) / len(x_vals)) ** 0.5
    std_y = (sum((y - mean_y) ** 2 for y in y_vals) / len(y_vals)) ** 0.5
    
    if std_x == 0 or std_y == 0:
        return 0.0
    
    return cov / (std_x * std_y)


def _interpret_tradeoffs(growth_profit: float, growth_stability: float, 
                        innovation_profit: float, innovation_stability: float) -> str:
    """Provide human-readable interpretation of tradeoffs"""
    tradeoffs = []
    
    if growth_profit < -0.3:
        tradeoffs.append("Growth and Profitability are in tension (pursue growth sacrifices short-term profit)")
    if growth_stability < -0.3:
        tradeoffs.append("Growth and Stability are in tension (pursue growth increases risk)")
    if innovation_profit < -0.3:
        tradeoffs.append("Innovation and Profitability are in tension (pursue innovation reduces short-term profit)")
    if innovation_stability < -0.3:
        tradeoffs.append("Innovation and Stability are in tension (pursue innovation increases risk)")
    
    if not tradeoffs:
        return "No significant tradeoffs detected - objectives are largely aligned"
    
    return "; ".join(tradeoffs)
