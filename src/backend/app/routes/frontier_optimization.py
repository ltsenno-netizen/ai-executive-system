"""
Frontier Optimization Routes (Step AD)

API endpoints for Pareto frontier optimization and analysis
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from ..services.frontier_optimization_service import FrontierOptimizationService

router = APIRouter()
service = FrontierOptimizationService()


@router.post("/frontier/optimize")
async def run_frontier_optimization():
    """
    Execute frontier optimization cycle
    
    Returns:
    - Shape analysis (convexity, density, extreme points)
    - Tradeoff gradients
    - Optimization recommendations
    - Estimated frontier improvement
    """
    try:
        result = service.run_frontier_optimization_cycle()
        
        return {
            "status": "success",
            "timestamp": result.timestamp.isoformat(),
            "shape_analysis": {
                "frontier_count": result.shape_report.frontier_count if result.shape_report else 0,
                "is_convex": result.shape_report.convexity.is_convex if result.shape_report else False,
                "convexity_ratio": result.shape_report.convexity.convexity_ratio if result.shape_report else 0.0,
                "overall_density": result.shape_report.density.overall_density if result.shape_report else 0.0,
                "clustering_coefficient": result.shape_report.density.clustering_coefficient if result.shape_report else 0.0,
                "extreme_points": len(result.shape_report.extreme_points) if result.shape_report else 0,
                "tradeoff_cliffs": len(result.shape_report.tradeoff_cliffs) if result.shape_report else 0,
                "optimization_readiness": result.shape_report.optimization_readiness if result.shape_report else "",
            },
            "gradient_analysis": {
                "total_gradients": result.gradient_report.total_gradients if result.gradient_report else 0,
                "key_gradients": len(result.gradient_report.key_gradients) if result.gradient_report else 0,
                "dominant_tradeoff": {
                    "from": result.gradient_report.dominant_tradeoff.from_objective,
                    "to": result.gradient_report.dominant_tradeoff.to_objective,
                    "magnitude": result.gradient_report.dominant_tradeoff.gradient_magnitude,
                } if result.gradient_report and result.gradient_report.dominant_tradeoff else None,
                "neutral_pairs": len(result.gradient_report.neutral_pairs) if result.gradient_report else 0,
                "quality_scores": result.frontier_quality_scores,
            },
            "optimization_opportunities": {
                "identified_clusters": len(result.optimization_report.identified_clusters) if result.optimization_report else 0,
                "redundant_candidates": result.optimization_report.redundant_count if result.optimization_report else 0,
                "identified_gaps": len(result.optimization_report.identified_gaps) if result.optimization_report else 0,
                "new_candidates_suggested": result.optimization_report.new_candidates_suggested if result.optimization_report else 0,
                "estimated_improvement": result.optimization_report.estimated_frontier_improvement if result.optimization_report else 0.0,
            },
            "frontier_potential": result.frontier_potential,
            "actionable_insights": result.actionable_insights,
            "recommendations": result.recommendations,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")


@router.get("/frontier/analysis")
async def get_frontier_shape_analysis():
    """
    Get detailed frontier shape analysis
    
    Returns:
    - Convexity characteristics
    - Extreme points
    - Tradeoff cliffs
    - Density distribution
    - Correlation patterns
    """
    try:
        result = service.run_frontier_optimization_cycle()
        
        if not result.shape_report:
            raise HTTPException(status_code=404, detail="No frontier available for analysis")
        
        return {
            "frontier_count": result.shape_report.frontier_count,
            "convexity": {
                "is_convex": result.shape_report.convexity.is_convex,
                "convexity_ratio": result.shape_report.convexity.convexity_ratio,
                "non_convex_regions": result.shape_report.convexity.non_convex_regions,
                "convex_hull_count": result.shape_report.convexity.convex_hull_count,
            },
            "extreme_points": [
                {
                    "objective": ep.objective,
                    "value": ep.value,
                    "is_maximal": ep.is_maximal,
                }
                for ep in result.shape_report.extreme_points
            ],
            "tradeoff_cliffs": [
                {
                    "from_objective": tc.from_objective,
                    "to_objective": tc.to_objective,
                    "slope_magnitude": tc.slope_magnitude,
                    "interpretation": tc.interpretation,
                }
                for tc in result.shape_report.tradeoff_cliffs[:10]  # Top 10
            ],
            "density": {
                "overall_density": result.shape_report.density.overall_density,
                "clustering_coefficient": result.shape_report.density.clustering_coefficient,
                "sparse_regions": result.shape_report.density.sparse_regions,
                "dense_regions": result.shape_report.density.dense_regions,
            },
            "correlations": [
                {
                    "objective_1": cp.objective_1,
                    "objective_2": cp.objective_2,
                    "correlation": cp.correlation,
                    "interpretation": cp.interpretation,
                }
                for cp in result.shape_report.correlations
            ],
            "shape_characteristics": result.shape_report.shape_characteristics,
            "optimization_readiness": result.shape_report.optimization_readiness,
            "gaps_and_opportunities": result.shape_report.gaps_and_opportunities,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.get("/frontier/gradients")
async def get_frontier_gradients():
    """
    Get tradeoff gradient analysis
    
    Returns:
    - Key gradients (top 5 by magnitude)
    - Gradient profiles
    - Dominant tradeoff
    - Neutral objective pairs
    """
    try:
        result = service.run_frontier_optimization_cycle()
        
        if not result.gradient_report:
            raise HTTPException(status_code=404, detail="No gradient data available")
        
        return {
            "total_gradients": result.gradient_report.total_gradients,
            "key_gradients": [
                {
                    "from_objective": kg.from_objective,
                    "to_objective": kg.to_objective,
                    "gradient": kg.gradient,
                    "gradient_magnitude": kg.gradient_magnitude,
                    "tradeoff_severity": kg.tradeoff_severity,
                    "interpretation": kg.interpretation,
                }
                for kg in result.gradient_report.key_gradients
            ],
            "dominant_tradeoff": {
                "from_objective": result.gradient_report.dominant_tradeoff.from_objective,
                "to_objective": result.gradient_report.dominant_tradeoff.to_objective,
                "gradient_magnitude": result.gradient_report.dominant_tradeoff.gradient_magnitude,
                "interpretation": result.gradient_report.dominant_tradeoff.interpretation,
            } if result.gradient_report.dominant_tradeoff else None,
            "neutral_pairs": result.gradient_report.neutral_pairs,
            "frontier_quality_scores": result.frontier_quality_scores,
            "actionable_insights": result.actionable_insights,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gradient analysis error: {str(e)}")


@router.get("/frontier/optimized")
async def get_frontier_optimization_recommendations():
    """
    Get frontier optimization recommendations
    
    Returns:
    - Identified clusters (redundancy)
    - Strategy gaps
    - New candidates to generate
    - Estimated frontier improvement
    """
    try:
        result = service.run_frontier_optimization_cycle()
        
        if not result.optimization_report:
            raise HTTPException(status_code=404, detail="No optimization data available")
        
        return {
            "identified_clusters": len(result.optimization_report.identified_clusters),
            "redundant_count": result.optimization_report.redundant_count,
            "identified_gaps": [
                {
                    "gap_id": gap.gap_id,
                    "gap_severity": gap.gap_severity,
                    "rationale": gap.rationale,
                    "suggested_scenario": gap.suggested_scenario,
                    "suggested_objective": gap.suggested_objective,
                }
                for gap in result.optimization_report.identified_gaps
            ],
            "new_candidates_suggested": result.optimization_report.new_candidates_suggested,
            "optimization_actions": result.optimization_report.optimization_actions,
            "estimated_frontier_improvement": result.optimization_report.estimated_frontier_improvement,
            "frontier_potential": result.frontier_potential,
            "recommendations": result.recommendations,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization recommendation error: {str(e)}")


@router.get("/frontier/health")
async def get_frontier_health():
    """
    Get frontier health score
    
    Returns:
    - Overall health score (0-1)
    - Should optimize (boolean)
    - Key issues if any
    """
    try:
        health_score = service.get_frontier_health_score()
        should_optimize = service.should_optimize_frontier()
        
        # Get details
        result = service.run_frontier_optimization_cycle()
        
        issues = []
        if result.shape_report:
            if result.shape_report.convexity.convexity_ratio < 0.7:
                issues.append("Non-convex frontier structure")
            if result.shape_report.density.overall_density < 0.2:
                issues.append("Low frontier density")
            issues.extend(result.shape_report.gaps_and_opportunities)
        
        return {
            "health_score": health_score,
            "status": "healthy" if health_score > 0.7 else "needs_optimization" if health_score > 0.4 else "critical",
            "should_optimize": should_optimize,
            "key_issues": issues,
            "last_optimization": service.get_optimization_summary(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")


@router.get("/frontier/history")
async def get_frontier_optimization_history(limit: int = 10):
    """
    Get frontier optimization history
    """
    try:
        history = service.get_optimization_history(limit)
        
        return {
            "count": len(history),
            "history": history,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval error: {str(e)}")


@router.get("/frontier/summary")
async def get_frontier_optimization_summary():
    """
    Get summary of current frontier state and optimization status
    """
    try:
        frontier = service.get_current_frontier()
        if not frontier:
            raise HTTPException(status_code=404, detail="No frontier available")
        
        result = service.run_frontier_optimization_cycle()
        health_score = service.get_frontier_health_score()
        
        return {
            "frontier_state": {
                "total_candidates": frontier.total_candidates,
                "frontier_points": frontier.frontier_count,
                "best_growth": frontier.best_growth,
                "best_profitability": frontier.best_profitability,
                "best_innovation": frontier.best_innovation,
                "best_stability": frontier.best_stability,
            },
            "shape_characteristics": result.shape_report.shape_characteristics if result.shape_report else "",
            "optimization_readiness": result.shape_report.optimization_readiness if result.shape_report else "",
            "health_score": health_score,
            "estimated_improvement_potential": result.frontier_potential.get("overall_optimization_potential", 0),
            "key_recommendations": result.recommendations[:5] if result.recommendations else [],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")
