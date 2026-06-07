from fastapi import APIRouter, HTTPException
from ..services.multi_objective_service import MultiObjectiveService

router = APIRouter(tags=["multi-objective"])
multi_objective_service = MultiObjectiveService()


@router.post("/multi-objective/run")
def run_multi_objective_analysis():
    """Run complete multi-objective optimization analysis"""
    frontier = multi_objective_service.generate_multi_objective_analysis()
    
    if not frontier:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate multi-objective analysis"
        )
    
    return {
        "message": f"Multi-objective analysis complete: {frontier.frontier_count} Pareto-optimal strategies identified",
        "frontier": frontier
    }


@router.get("/multi-objective/frontier")
def get_frontier():
    """Get latest Pareto frontier"""
    frontier = multi_objective_service.get_frontier()
    
    if not frontier:
        raise HTTPException(
            status_code=404,
            detail="No frontier analysis available"
        )
    
    return frontier


@router.get("/multi-objective/candidates")
def get_all_candidates():
    """Get all evaluated candidates"""
    candidates = multi_objective_service.get_candidates()
    
    if not candidates:
        raise HTTPException(
            status_code=404,
            detail="No candidates available"
        )
    
    return {
        "count": len(candidates),
        "candidates": candidates
    }


@router.get("/multi-objective/frontier-candidates")
def get_frontier_candidates():
    """Get only Pareto-optimal candidates"""
    candidates = multi_objective_service.get_frontier_candidates()
    
    if not candidates:
        raise HTTPException(
            status_code=404,
            detail="No frontier candidates available"
        )
    
    return {
        "count": len(candidates),
        "frontier_candidates": candidates
    }
