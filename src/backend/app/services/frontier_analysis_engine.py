"""
Frontier Analysis Engine (Step AD)

Analyzes the shape and structure of Pareto frontiers to identify:
- Convexity/Non-convexity
- Extreme points (points with extreme values in objectives)
- Tradeoff cliffs (areas with steep tradeoffs)
- Density distribution
- Correlation patterns
"""

from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, Field
import numpy as np
from ..models.multi_objective_model import ParetoFrontier, StrategyCandidate, ObjectiveVector


class ExtremePoint(BaseModel):
    """Represents an extreme point in the Pareto frontier"""
    candidate_index: int = Field(..., description="Index in frontier candidates")
    objective: str = Field(..., description="Objective dimension that is extreme (GROWTH, PROFITABILITY, INNOVATION, STABILITY)")
    value: float = Field(..., description="Value of the extreme")
    is_maximal: bool = Field(..., description="True if this is maximum in dimension, False if minimum")


class TradeoffCliff(BaseModel):
    """Represents a region where tradeoffs are steep"""
    from_objective: str = Field(..., description="Source objective")
    to_objective: str = Field(..., description="Target objective")
    cliff_start_idx: int = Field(..., description="Index where cliff begins")
    cliff_end_idx: int = Field(..., description="Index where cliff ends")
    slope_magnitude: float = Field(..., description="Absolute value of slope")
    interpretation: str = Field(..., description="Human-readable description of tradeoff")


class FrontierDensity(BaseModel):
    """Distribution density of frontier candidates"""
    overall_density: float = Field(..., description="Number of frontier points / (objective space volume), 0-1")
    sparse_regions: List[str] = Field(..., description="Regions with low density")
    dense_regions: List[str] = Field(..., description="Regions with high density")
    clustering_coefficient: float = Field(..., ge=0.0, le=1.0, description="How clustered candidates are (0=spread, 1=clustered)")


class CorrelationPattern(BaseModel):
    """Correlation between objectives in frontier"""
    objective_1: str
    objective_2: str
    correlation: float = Field(..., ge=-1.0, le=1.0, description="Pearson correlation coefficient")
    interpretation: str = Field(..., description="Human-readable correlation description")


class ConvexityAnalysis(BaseModel):
    """Analysis of frontier convexity"""
    is_convex: bool = Field(..., description="Whether frontier exhibits convexity")
    convexity_ratio: float = Field(..., ge=0.0, le=1.0, description="Ratio of convex to total points (0=non-convex, 1=fully convex)")
    non_convex_regions: List[Tuple[int, int]] = Field(default_factory=list, description="Index ranges with non-convexity")
    convex_hull_count: int = Field(..., description="Number of points on convex hull (2D projected)")


class FrontierShapeReport(BaseModel):
    """Complete shape analysis of Pareto frontier"""
    frontier_count: int = Field(..., description="Number of frontier candidates")
    
    # Shape characteristics
    convexity: ConvexityAnalysis = Field(..., description="Convexity analysis")
    extreme_points: List[ExtremePoint] = Field(..., description="Extreme points in each objective")
    tradeoff_cliffs: List[TradeoffCliff] = Field(..., description="Regions with steep tradeoffs")
    
    # Distribution
    density: FrontierDensity = Field(..., description="Density distribution")
    
    # Relationships
    correlations: List[CorrelationPattern] = Field(..., description="Objective correlations")
    
    # Overall assessment
    shape_characteristics: str = Field(..., description="Description of frontier shape")
    optimization_readiness: str = Field(..., description="Assessment of frontier quality for optimization")
    gaps_and_opportunities: List[str] = Field(..., description="Identified gaps or opportunities in frontier")


def extract_objective_vectors(frontier: ParetoFrontier) -> np.ndarray:
    """Extract frontier candidates as 4D numpy array"""
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


def compute_convexity_analysis(vectors: np.ndarray) -> ConvexityAnalysis:
    """Analyze convexity of frontier (simplified 2D analysis on growth-profitability plane)"""
    if len(vectors) < 3:
        return ConvexityAnalysis(
            is_convex=False,
            convexity_ratio=0.5,
            non_convex_regions=[],
            convex_hull_count=len(vectors)
        )
    
    # Project to 2D: growth vs profitability
    points_2d = vectors[:, [0, 1]]  # growth, profitability
    
    # Sort by growth
    sorted_indices = np.argsort(points_2d[:, 0])
    sorted_points = points_2d[sorted_indices]
    
    # Check convexity by computing slopes
    non_convex_count = 0
    non_convex_regions = []
    
    for i in range(len(sorted_points) - 2):
        p1 = sorted_points[i]
        p2 = sorted_points[i + 1]
        p3 = sorted_points[i + 2]
        
        # Cross product to check if point is "above" line
        cross = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
        
        if cross < -0.01:  # Non-convex (slightly below line)
            non_convex_count += 1
            if not non_convex_regions or non_convex_regions[-1][1] != i:
                non_convex_regions.append((i, i + 1))
            else:
                non_convex_regions[-1] = (non_convex_regions[-1][0], i + 1)
    
    convexity_ratio = 1.0 - (non_convex_count / max(1, len(sorted_points) - 2))
    is_convex = convexity_ratio > 0.8
    
    return ConvexityAnalysis(
        is_convex=is_convex,
        convexity_ratio=convexity_ratio,
        non_convex_regions=non_convex_regions,
        convex_hull_count=len(sorted_points)
    )


def find_extreme_points(frontier: ParetoFrontier, vectors: np.ndarray) -> List[ExtremePoint]:
    """Identify extreme points in each objective dimension"""
    objectives = ["growth", "profitability", "innovation", "stability"]
    extreme_points = []
    
    for dim, obj_name in enumerate(objectives):
        # Max point
        max_idx = np.argmax(vectors[:, dim])
        extreme_points.append(ExtremePoint(
            candidate_index=frontier.frontier_indices[max_idx],
            objective=obj_name.upper(),
            value=float(vectors[max_idx, dim]),
            is_maximal=True
        ))
        
        # Min point (only if < max by significant margin)
        min_idx = np.argmin(vectors[:, dim])
        if vectors[min_idx, dim] < vectors[max_idx, dim] * 0.8:
            extreme_points.append(ExtremePoint(
                candidate_index=frontier.frontier_indices[min_idx],
                objective=obj_name.upper(),
                value=float(vectors[min_idx, dim]),
                is_maximal=False
            ))
    
    return extreme_points


def identify_tradeoff_cliffs(frontier: ParetoFrontier, vectors: np.ndarray) -> List[TradeoffCliff]:
    """Identify regions where tradeoffs are steep"""
    cliffs = []
    objectives = ["GROWTH", "PROFITABILITY", "INNOVATION", "STABILITY"]
    
    # Analyze 2D projections
    for i in range(4):
        for j in range(i + 1, 4):
            points_2d = vectors[:, [i, j]]
            
            # Sort by first objective
            sorted_indices = np.argsort(points_2d[:, 0])
            sorted_points = points_2d[sorted_indices]
            
            # Compute slopes
            slopes = []
            for k in range(len(sorted_points) - 1):
                dx = sorted_points[k + 1, 0] - sorted_points[k, 0]
                dy = sorted_points[k + 1, 1] - sorted_points[k, 1]
                
                if dx > 0.01:
                    slope = abs(dy / dx)
                    slopes.append((k, slope))
            
            # Find steep slopes (>75th percentile)
            if slopes:
                slope_values = [s[1] for s in slopes]
                threshold = np.percentile(slope_values, 75)
                
                for idx, slope in slopes:
                    if slope > threshold:
                        cliffs.append(TradeoffCliff(
                            from_objective=objectives[i],
                            to_objective=objectives[j],
                            cliff_start_idx=frontier.frontier_indices[sorted_indices[idx]],
                            cliff_end_idx=frontier.frontier_indices[sorted_indices[idx + 1]],
                            slope_magnitude=float(slope),
                            interpretation=f"Steep tradeoff between {objectives[i]} ({sorted_points[idx, 0]:.1f}) and {objectives[j]} ({sorted_points[idx, 1]:.2f})"
                        ))
    
    return cliffs


def analyze_frontier_density(vectors: np.ndarray) -> FrontierDensity:
    """Analyze spatial distribution of frontier candidates"""
    n = len(vectors)
    
    # Compute pairwise distances
    if n > 1:
        distances = []
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(vectors[i] - vectors[j])
                distances.append(dist)
        
        avg_distance = np.mean(distances)
        min_distance = np.min(distances)
        max_distance = np.max(distances)
        
        # Clustering coefficient (inverse of average distance)
        clustering_coefficient = min(1.0, 1.0 / (1.0 + avg_distance))
    else:
        clustering_coefficient = 0.5
        avg_distance = 0.0
    
    # Estimate objective space volume (simplified)
    mins = np.min(vectors, axis=0)
    maxs = np.max(vectors, axis=0)
    ranges = maxs - mins
    volume = np.prod(ranges) if np.all(ranges > 0) else 1.0
    
    density = n / max(1.0, volume)
    overall_density = min(1.0, density / 10.0)  # Normalize
    
    sparse_regions = []
    dense_regions = []
    
    if avg_distance > 20:
        sparse_regions.append("High dimensional spread")
    if clustering_coefficient > 0.7:
        dense_regions.append("Clustered candidates")
    
    return FrontierDensity(
        overall_density=float(overall_density),
        sparse_regions=sparse_regions,
        dense_regions=dense_regions,
        clustering_coefficient=float(clustering_coefficient)
    )


def compute_correlations(vectors: np.ndarray) -> List[CorrelationPattern]:
    """Compute correlations between objective dimensions"""
    objectives = ["GROWTH", "PROFITABILITY", "INNOVATION", "STABILITY"]
    patterns = []
    
    for i in range(4):
        for j in range(i + 1, 4):
            # Pearson correlation
            corr = np.corrcoef(vectors[:, i], vectors[:, j])[0, 1]
            
            if np.isnan(corr):
                corr = 0.0
            
            # Interpretation
            if corr > 0.5:
                interp = f"{objectives[i]} and {objectives[j]} are positively correlated - achieving one helps achieve the other"
            elif corr < -0.5:
                interp = f"{objectives[i]} and {objectives[j]} are negatively correlated - strong tradeoff exists"
            else:
                interp = f"{objectives[i]} and {objectives[j]} are largely independent"
            
            patterns.append(CorrelationPattern(
                objective_1=objectives[i],
                objective_2=objectives[j],
                correlation=float(corr),
                interpretation=interp
            ))
    
    return patterns


def analyze_frontier_shape(frontier: ParetoFrontier) -> FrontierShapeReport:
    """
    Main analysis function: generate complete shape report for frontier
    """
    if not frontier.frontier_indices:
        return FrontierShapeReport(
            frontier_count=0,
            convexity=ConvexityAnalysis(is_convex=False, convexity_ratio=0.0, non_convex_regions=[], convex_hull_count=0),
            extreme_points=[],
            tradeoff_cliffs=[],
            density=FrontierDensity(overall_density=0.0, sparse_regions=[], dense_regions=[], clustering_coefficient=0.5),
            correlations=[],
            shape_characteristics="Empty frontier",
            optimization_readiness="Cannot optimize empty frontier",
            gaps_and_opportunities=[]
        )
    
    # Extract vectors
    vectors = extract_objective_vectors(frontier)
    
    # Analyze components
    convexity = compute_convexity_analysis(vectors)
    extreme_points = find_extreme_points(frontier, vectors)
    cliffs = identify_tradeoff_cliffs(frontier, vectors)
    density = analyze_frontier_density(vectors)
    correlations = compute_correlations(vectors)
    
    # Generate shape characteristics
    shape_chars = []
    if convexity.is_convex:
        shape_chars.append("Convex frontier - good tradeoff structure")
    else:
        shape_chars.append(f"Non-convex frontier ({convexity.convexity_ratio:.1%} convex)")
    
    if density.clustering_coefficient > 0.7:
        shape_chars.append("Highly clustered candidates - consider diversification")
    elif density.clustering_coefficient < 0.3:
        shape_chars.append("Widely distributed candidates - good coverage")
    else:
        shape_chars.append("Moderate distribution of candidates")
    
    if len(cliffs) > 3:
        shape_chars.append(f"Multiple steep tradeoff regions ({len(cliffs)} identified)")
    
    # Optimization readiness assessment
    readiness = "Ready for optimization"
    if len(frontier.frontier_indices) < 3:
        readiness = "Insufficient frontier points for optimization"
    elif convexity.convexity_ratio < 0.5:
        readiness = "Non-convex frontier - may need frontier reconstruction"
    elif density.overall_density < 0.1:
        readiness = "Low density frontier - opportunities for new candidates"
    
    # Identify gaps
    gaps = []
    
    # Check for unbalanced objectives
    growth_range = frontier.best_growth
    prof_range = frontier.best_profitability
    if growth_range > prof_range * 10:
        gaps.append("Growth-dominated frontier - consider profitability strategies")
    
    if len(cliffs) > 5:
        gaps.append("Many steep tradeoffs - consider intermediate strategies")
    
    if density.overall_density < 0.2:
        gaps.append("Sparse coverage - generate candidates in lower-density regions")
    
    return FrontierShapeReport(
        frontier_count=len(frontier.frontier_indices),
        convexity=convexity,
        extreme_points=extreme_points,
        tradeoff_cliffs=cliffs,
        density=density,
        correlations=correlations,
        shape_characteristics="; ".join(shape_chars),
        optimization_readiness=readiness,
        gaps_and_opportunities=gaps
    )
