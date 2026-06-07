"""
Tradeoff Gradient Estimation (Step AD)

Computes gradients along Pareto frontier to estimate rates of change
between objectives:
- dGrowth/dStability
- dInnovation/dProfitability
- etc.

This enables understanding HOW MUCH of one objective must be sacrificed
to gain another.
"""

from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel, Field
import numpy as np
from ..models.multi_objective_model import ParetoFrontier, ObjectiveVector


class TradeoffGradient(BaseModel):
    """Represents rate of change between two objectives along frontier"""
    from_objective: str = Field(..., description="Source objective (e.g., GROWTH)")
    to_objective: str = Field(..., description="Target objective (e.g., STABILITY)")
    gradient: float = Field(..., description="d(target)/d(source) - rate of change")
    gradient_magnitude: float = Field(..., ge=0.0, description="Absolute value of gradient")
    tradeoff_severity: str = Field(..., description="'steep', 'moderate', or 'gentle'")
    interpretation: str = Field(..., description="Human-readable interpretation")


class TradeoffProfile(BaseModel):
    """Complete tradeoff profile between two objectives"""
    from_objective: str
    to_objective: str
    local_gradients: List[float] = Field(..., description="Gradients at each frontier point")
    average_gradient: float = Field(..., description="Average gradient")
    min_gradient: float = Field(..., description="Shallowest tradeoff")
    max_gradient: float = Field(..., description="Steepest tradeoff")
    gradient_stability: float = Field(..., ge=0.0, le=1.0, description="How consistent is the gradient (0=varies wildly, 1=constant)")


class FrontierGradientReport(BaseModel):
    """Complete gradient analysis of Pareto frontier"""
    total_gradients: int = Field(..., description="Number of gradient pairs analyzed")
    key_gradients: List[TradeoffGradient] = Field(..., description="Most significant tradeoff gradients")
    all_gradients: Dict[str, TradeoffGradient] = Field(..., description="All gradients by 'obj1_obj2' key")
    gradient_profiles: Dict[str, TradeoffProfile] = Field(..., description="Detailed profiles")
    dominant_tradeoff: Optional[TradeoffGradient] = Field(..., description="Most significant tradeoff")
    neutral_pairs: List[Tuple[str, str]] = Field(..., description="Objective pairs with near-zero correlation")


def extract_frontier_vectors(frontier: ParetoFrontier) -> np.ndarray:
    """Extract frontier vectors as 4D array"""
    frontier_candidates = [frontier.candidates[i] for i in frontier.frontier_indices]
    
    vectors = np.array([
        [
            c.objective_vector.growth,
            c.objective_vector.profitability,
            c.objective_vector.innovation,
            c.objective_vector.stability
        ]
        for c in frontier_candidates
    ])
    
    return vectors


def compute_local_gradients(
    vectors: np.ndarray,
    from_idx: int,
    to_idx: int
) -> List[float]:
    """
    Compute local gradients at each frontier point
    
    Estimates: d(objective_to) / d(objective_from)
    """
    if len(vectors) < 2:
        return []
    
    gradients = []
    
    for i in range(len(vectors)):
        # Find closest neighbors
        distances = np.sum((vectors - vectors[i]) ** 2, axis=1)
        distances[i] = np.inf
        
        if len(distances) < 2:
            continue
        
        # Two nearest neighbors
        nearest_indices = np.argsort(distances)[:2]
        
        # Compute local gradient
        dx = vectors[nearest_indices[0], from_idx] - vectors[i, from_idx]
        dy = vectors[nearest_indices[0], to_idx] - vectors[i, to_idx]
        
        if abs(dx) > 0.01:
            gradient = dy / dx
            gradients.append(gradient)
    
    return gradients


def compute_tradeoff_gradients(frontier: ParetoFrontier) -> FrontierGradientReport:
    """
    Main function: compute all tradeoff gradients
    """
    if not frontier.frontier_indices or len(frontier.frontier_indices) < 2:
        return FrontierGradientReport(
            total_gradients=0,
            key_gradients=[],
            all_gradients={},
            gradient_profiles={},
            dominant_tradeoff=None,
            neutral_pairs=[]
        )
    
    vectors = extract_frontier_vectors(frontier)
    objectives = ["GROWTH", "PROFITABILITY", "INNOVATION", "STABILITY"]
    objective_indices = {obj: i for i, obj in enumerate(objectives)}
    
    all_gradients = {}
    gradient_profiles = {}
    dominant_tradeoff = None
    max_magnitude = 0.0
    
    # Compute gradients for all pairs
    for i, obj1 in enumerate(objectives):
        for j, obj2 in enumerate(objectives):
            if i >= j:
                continue
            
            from_idx = i
            to_idx = j
            
            # Compute local gradients
            local_gradients = compute_local_gradients(vectors, from_idx, to_idx)
            
            if not local_gradients:
                continue
            
            local_gradients_arr = np.array(local_gradients)
            avg_gradient = float(np.mean(local_gradients_arr))
            min_gradient = float(np.min(local_gradients_arr))
            max_gradient = float(np.max(local_gradients_arr))
            
            # Gradient stability (inverse of coefficient of variation)
            if abs(np.mean(local_gradients_arr)) > 0.01:
                cv = np.std(local_gradients_arr) / abs(np.mean(local_gradients_arr))
                stability = max(0.0, 1.0 - cv)
            else:
                stability = 1.0
            
            # Determine tradeoff severity
            magnitude = abs(avg_gradient)
            if magnitude > 1.0:
                severity = "steep"
            elif magnitude > 0.1:
                severity = "moderate"
            else:
                severity = "gentle"
            
            # Create gradient
            gradient = TradeoffGradient(
                from_objective=obj1,
                to_objective=obj2,
                gradient=avg_gradient,
                gradient_magnitude=magnitude,
                tradeoff_severity=severity,
                interpretation=f"To gain 1 unit of {obj2}, sacrifice ~{abs(avg_gradient):.2f} units of {obj1}"
            )
            
            all_gradients[f"{obj1}_{obj2}"] = gradient
            
            gradient_profiles[f"{obj1}_{obj2}"] = TradeoffProfile(
                from_objective=obj1,
                to_objective=obj2,
                local_gradients=[float(g) for g in local_gradients_arr],
                average_gradient=avg_gradient,
                min_gradient=min_gradient,
                max_gradient=max_gradient,
                gradient_stability=float(stability)
            )
            
            # Track dominant tradeoff
            if magnitude > max_magnitude:
                max_magnitude = magnitude
                dominant_tradeoff = gradient
    
    # Select key gradients (top 5 by magnitude)
    key_gradients = sorted(
        all_gradients.values(),
        key=lambda g: g.gradient_magnitude,
        reverse=True
    )[:5]
    
    # Identify neutral pairs (gradients near zero)
    neutral_pairs = []
    for pair_key, gradient in all_gradients.items():
        if gradient.gradient_magnitude < 0.05:
            objs = pair_key.split("_")
            neutral_pairs.append((objs[0], objs[1]))
    
    return FrontierGradientReport(
        total_gradients=len(all_gradients),
        key_gradients=key_gradients,
        all_gradients=all_gradients,
        gradient_profiles=gradient_profiles,
        dominant_tradeoff=dominant_tradeoff,
        neutral_pairs=neutral_pairs
    )


def estimate_frontier_quality(gradient_report: FrontierGradientReport) -> Dict[str, float]:
    """
    Estimate frontier quality based on gradient characteristics
    
    Returns scores for different quality metrics
    """
    scores = {}
    
    # Tradeoff complexity: higher is better (more diverse tradeoffs)
    scores["tradeoff_diversity"] = min(1.0, len(gradient_report.key_gradients) / 6.0)
    
    # Tradeoff consistency: higher is better (stable gradients)
    if gradient_report.gradient_profiles:
        avg_stability = np.mean([p.gradient_stability for p in gradient_report.gradient_profiles.values()])
        scores["gradient_stability"] = float(avg_stability)
    else:
        scores["gradient_stability"] = 0.5
    
    # Balance: lower is better (gradients not too steep or shallow)
    if gradient_report.key_gradients:
        magnitudes = [g.gradient_magnitude for g in gradient_report.key_gradients]
        # Ideal: around 0.5-1.0
        balance = 1.0 - abs(np.mean(magnitudes) - 0.5) / 2.0
        scores["gradient_balance"] = max(0.0, min(1.0, balance))
    else:
        scores["gradient_balance"] = 0.5
    
    # Neutral relationships: higher is better (independent objectives)
    if gradient_report.total_gradients > 0:
        neutral_ratio = len(gradient_report.neutral_pairs) / gradient_report.total_gradients
        scores["objective_independence"] = float(neutral_ratio)
    else:
        scores["objective_independence"] = 0.0
    
    return scores


def extract_actionable_insights(gradient_report: FrontierGradientReport) -> List[str]:
    """
    Extract actionable insights from gradient analysis
    """
    insights = []
    
    if not gradient_report.key_gradients:
        return ["Insufficient frontier data for gradient analysis"]
    
    # Identify most severe tradeoff
    if gradient_report.dominant_tradeoff:
        insights.append(
            f"Most severe tradeoff: {gradient_report.dominant_tradeoff.from_objective} vs "
            f"{gradient_report.dominant_tradeoff.to_objective} "
            f"(gradient: {gradient_report.dominant_tradeoff.gradient_magnitude:.2f})"
        )
    
    # Identify steep vs gentle tradeoffs
    steep_count = len([g for g in gradient_report.key_gradients if g.tradeoff_severity == "steep"])
    gentle_count = len([g for g in gradient_report.key_gradients if g.tradeoff_severity == "gentle"])
    
    if steep_count > gentle_count:
        insights.append("Frontier shows many steep tradeoffs - consider diversifying strategies")
    elif gentle_count > steep_count:
        insights.append("Frontier shows many gentle tradeoffs - opportunities for win-win strategies")
    
    # Identify independent objectives
    if gradient_report.neutral_pairs:
        neutral_str = ", ".join([f"{a}-{b}" for a, b in gradient_report.neutral_pairs[:3]])
        insights.append(f"Independent objectives detected: {neutral_str}")
    
    return insights
