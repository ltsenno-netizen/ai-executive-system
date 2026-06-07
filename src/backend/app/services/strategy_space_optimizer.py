"""
Strategy Space Optimizer (Step AD)

Uses frontier analysis and tradeoff gradients to:
- Remove redundant/dominated strategy clusters
- Generate new candidates in promising directions
- Fill gaps in the frontier
- Improve overall frontier coverage and quality
"""

from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, Field
import numpy as np
from datetime import datetime

from ..models.multi_objective_model import (
    ParetoFrontier,
    StrategyCandidate,
    ObjectiveVector,
    ScenarioType,
)
from ..models.self_optimization_model import OptimizationObjective
from .frontier_analysis_engine import FrontierShapeReport, ExtremePoint
from .tradeoff_gradient import FrontierGradientReport, TradeoffGradient


class StrategyGap(BaseModel):
    """Represents a gap in strategy space"""
    gap_id: str = Field(..., description="Unique identifier")
    location: ObjectiveVector = Field(..., description="Target objective values for gap")
    gap_severity: str = Field(..., description="'critical', 'moderate', or 'minor'")
    rationale: str = Field(..., description="Why this gap should be filled")
    suggested_scenario: str = Field(..., description="Recommended scenario type")
    suggested_objective: str = Field(..., description="Recommended optimization objective")


class CandidateCluster(BaseModel):
    """Represents a cluster of similar candidates"""
    cluster_id: int = Field(..., description="Cluster index")
    candidate_indices: List[int] = Field(..., description="Indices in frontier")
    center: ObjectiveVector = Field(..., description="Cluster center")
    radius: float = Field(..., description="Average distance to center")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Internal similarity (0-1)")
    representation_candidate: int = Field(..., description="Index of best representative")


class StrategySpaceOptimizationReport(BaseModel):
    """Report on strategy space optimization recommendations"""
    identified_clusters: List[CandidateCluster] = Field(..., description="Redundant candidate clusters")
    redundant_count: int = Field(..., description="Number of candidates recommended for removal")
    identified_gaps: List[StrategyGap] = Field(..., description="Identified strategy gaps")
    new_candidates_suggested: int = Field(..., description="Number of new candidates to generate")
    optimization_actions: List[str] = Field(..., description="Recommended actions")
    estimated_frontier_improvement: float = Field(..., ge=0.0, le=1.0, description="Expected quality improvement (0-1)")


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


def identify_redundant_clusters(frontier: ParetoFrontier, vectors: np.ndarray) -> List[CandidateCluster]:
    """Identify clusters of similar candidates"""
    if len(vectors) < 4:
        return []
    
    # Simple clustering: find groups within distance threshold
    clusters = []
    assigned = set()
    threshold = 5.0  # Distance threshold
    
    for i, idx in enumerate(frontier.frontier_indices):
        if i in assigned:
            continue
        
        # Start new cluster
        cluster_members = [i]
        assigned.add(i)
        
        # Find members within threshold
        for j in range(i + 1, len(vectors)):
            if j in assigned:
                continue
            
            dist = np.linalg.norm(vectors[i] - vectors[j])
            if dist < threshold:
                cluster_members.append(j)
                assigned.add(j)
        
        # Only report if cluster has multiple members
        if len(cluster_members) > 1:
            cluster_vectors = vectors[cluster_members]
            center = np.mean(cluster_vectors, axis=0)
            radius = np.mean([np.linalg.norm(v - center) for v in cluster_vectors])
            
            # Similarity: inverse of internal variance
            if np.std(cluster_vectors) > 0:
                similarity = 1.0 / (1.0 + np.std(cluster_vectors))
            else:
                similarity = 1.0
            
            # Find best representative (closest to center)
            rep_idx = cluster_members[np.argmin([np.linalg.norm(vectors[m] - center) for m in cluster_members])]
            
            clusters.append(CandidateCluster(
                cluster_id=len(clusters),
                candidate_indices=[frontier.frontier_indices[m] for m in cluster_members],
                center=ObjectiveVector(
                    growth=float(center[0]),
                    profitability=float(center[1]),
                    innovation=float(center[2]),
                    stability=float(center[3])
                ),
                radius=float(radius),
                similarity=float(min(1.0, similarity)),
                representation_candidate=frontier.frontier_indices[rep_idx]
            ))
    
    return clusters


def identify_strategy_gaps(
    frontier: ParetoFrontier,
    vectors: np.ndarray,
    shape_report: FrontierShapeReport
) -> List[StrategyGap]:
    """Identify gaps in strategy space"""
    gaps = []
    gap_count = 0
    
    # Gap 1: Between growth and stability
    if frontier.best_growth > frontier.best_stability * 10:
        # Check if there's a candidate balancing both
        balance_score = []
        for v in vectors:
            balance = min(v[0], v[3]) / max(v[0], v[3]) if max(v[0], v[3]) > 0 else 0
            balance_score.append(balance)
        
        if max(balance_score) < 0.5:
            gaps.append(StrategyGap(
                gap_id=f"GAP_{gap_count}",
                location=ObjectiveVector(
                    growth=float(frontier.best_growth * 0.7),
                    profitability=float(frontier.best_profitability * 0.7),
                    innovation=0.6,
                    stability=0.7
                ),
                gap_severity="moderate",
                rationale="Missing balanced growth-stability strategy",
                suggested_scenario="BALANCED",
                suggested_objective="STABILITY"
            ))
            gap_count += 1
    
    # Gap 2: High innovation with stability
    max_innovation_idx = np.argmax(vectors[:, 2])
    if vectors[max_innovation_idx, 3] < 0.6:  # High innovation but low stability
        gaps.append(StrategyGap(
            gap_id=f"GAP_{gap_count}",
            location=ObjectiveVector(
                growth=float(vectors[max_innovation_idx, 0] * 0.8),
                profitability=float(vectors[max_innovation_idx, 1] * 0.8),
                innovation=0.85,
                stability=0.75
            ),
            gap_severity="critical",
            rationale="Gap between innovation and stability - need sustainable innovation",
            suggested_scenario="INNOVATIVE",
            suggested_objective="INNOVATION"
        ))
        gap_count += 1
    
    # Gap 3: In sparse regions
    if len(shape_report.density.sparse_regions) > 0:
        # Generate gap in center of objective space
        center = np.mean(vectors, axis=0)
        gaps.append(StrategyGap(
            gap_id=f"GAP_{gap_count}",
            location=ObjectiveVector(
                growth=float(center[0]),
                profitability=float(center[1]),
                innovation=float(center[2]),
                stability=float(center[3])
            ),
            gap_severity="minor",
            rationale="Sparse region - increase density for better coverage",
            suggested_scenario="BALANCED",
            suggested_objective="GROWTH"
        ))
        gap_count += 1
    
    return gaps


def generate_new_candidates_for_gap(
    gap: StrategyGap,
    frontier: ParetoFrontier
) -> Optional[StrategyCandidate]:
    """
    Generate a new candidate strategy to fill a gap
    
    In real implementation, this would call strategy generation service
    For now, returns None (indicating need for external generation)
    """
    # This would integrate with strategy_generation_service in full implementation
    
    candidate = StrategyCandidate(
        scenario_type=ScenarioType(gap.suggested_scenario),
        optimization_objective=OptimizationObjective(gap.suggested_objective),
        scenario_summary=f"Generated to fill gap: {gap.rationale}",
        objective_vector=gap.location,
        roadmap_title=f"Gap-filling strategy ({gap.gap_id})",
        strategy_count=4,
        key_focus="Balanced approach",
        expected_risks=["Requires new capability development"],
        expected_benefits=["Fills frontier gap", "Improves coverage"]
    )
    
    return candidate


def optimize_strategy_space(
    frontier: ParetoFrontier,
    shape_report: Optional[FrontierShapeReport] = None,
    gradient_report: Optional[FrontierGradientReport] = None
) -> StrategySpaceOptimizationReport:
    """
    Main optimization function
    """
    if not frontier.frontier_indices:
        return StrategySpaceOptimizationReport(
            identified_clusters=[],
            redundant_count=0,
            identified_gaps=[],
            new_candidates_suggested=0,
            optimization_actions=[],
            estimated_frontier_improvement=0.0
        )
    
    vectors = extract_frontier_vectors(frontier)
    
    # Generate shape report if not provided
    if shape_report is None:
        from .frontier_analysis_engine import analyze_frontier_shape
        shape_report = analyze_frontier_shape(frontier)
    
    # Identify redundant clusters
    clusters = identify_redundant_clusters(frontier, vectors)
    redundant_count = len([c for c in clusters if c.similarity > 0.7])
    
    # Identify gaps
    gaps = identify_strategy_gaps(frontier, vectors, shape_report)
    
    # Generate new candidates for gaps
    new_candidates_suggested = len(gaps)
    
    # Build recommendations
    actions = []
    
    if redundant_count > 0:
        actions.append(f"Remove {redundant_count} redundant candidates from clusters")
    
    if len(gaps) > 0:
        actions.append(f"Generate {len(gaps)} new candidates to fill identified gaps")
    
    if shape_report.convexity.convexity_ratio < 0.7:
        actions.append("Reconstruct frontier for better convexity")
    
    if shape_report.density.overall_density < 0.2:
        actions.append("Increase frontier density in sparse regions")
    
    # Estimate improvement
    improvement = 0.0
    improvement += min(0.2, redundant_count * 0.05)  # Removing redundancy
    improvement += min(0.3, len(gaps) * 0.05)  # Filling gaps
    if shape_report.convexity.convexity_ratio < 0.7:
        improvement += 0.15  # Reconstruction benefit
    
    improvement = min(0.8, improvement)  # Cap at 0.8
    
    return StrategySpaceOptimizationReport(
        identified_clusters=clusters,
        redundant_count=redundant_count,
        identified_gaps=gaps,
        new_candidates_suggested=new_candidates_suggested,
        optimization_actions=actions,
        estimated_frontier_improvement=float(improvement)
    )


def generate_optimized_frontier(
    frontier: ParetoFrontier,
    optimization_report: StrategySpaceOptimizationReport
) -> ParetoFrontier:
    """
    Generate improved frontier by:
    1. Removing redundant candidates
    2. Adding new candidates for gaps
    """
    if not optimization_report.identified_clusters and not optimization_report.identified_gaps:
        return frontier
    
    # Start with filtered candidates (remove redundancy)
    filtered_indices = set(frontier.frontier_indices)
    
    for cluster in optimization_report.identified_clusters:
        if len(cluster.candidate_indices) > 1:
            # Keep only the representative
            members = cluster.candidate_indices
            rep = cluster.representation_candidate
            
            for m in members:
                if m != rep:
                    filtered_indices.discard(m)
    
    # Create new frontier
    optimized_frontier = frontier.copy()
    optimized_frontier.frontier_indices = list(filtered_indices)
    optimized_frontier.frontier_count = len(filtered_indices)
    
    return optimized_frontier


def estimate_frontier_potential(
    shape_report: FrontierShapeReport,
    gradient_report: Optional[FrontierGradientReport] = None
) -> Dict[str, float]:
    """
    Estimate frontier's potential for optimization
    """
    scores = {}
    
    # Convexity potential: non-convex has more potential
    scores["reconstruction_potential"] = 1.0 - shape_report.convexity.convexity_ratio
    
    # Density potential: sparse has more potential
    scores["density_potential"] = 1.0 - min(1.0, shape_report.density.overall_density)
    
    # Gap filling potential: based on range of objectives
    objective_ranges = []
    for gap in shape_report.gaps_and_opportunities:
        if "opportunities" in gap.lower():
            scores["gap_filling_potential"] = min(1.0, 0.5 + len(shape_report.gaps_and_opportunities) * 0.1)
            break
    else:
        scores["gap_filling_potential"] = 0.3
    
    # Overall potential
    scores["overall_optimization_potential"] = np.mean([
        scores["reconstruction_potential"],
        scores["density_potential"],
        scores["gap_filling_potential"]
    ])
    
    return scores
