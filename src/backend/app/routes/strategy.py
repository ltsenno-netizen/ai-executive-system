from fastapi import APIRouter, HTTPException
from ..models.self_optimization_model import OptimizationObjective
from ..services.strategy_service import StrategyService

router = APIRouter(tags=["strategy"])
strategy_service = StrategyService()


@router.post("/strategy/generate/{objective}")
def generate_strategy_roadmap(objective: str):
    """Generate strategy roadmap for objective"""
    try:
        obj = OptimizationObjective(objective)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid objective: {objective}"
        )
    
    roadmap = strategy_service.generate_strategy_roadmap(obj)
    
    if not roadmap:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate strategy roadmap"
        )
    
    return {
        "message": f"Generated strategy roadmap for objective: {objective}",
        "roadmap": roadmap
    }


@router.get("/strategy/latest")
def get_latest_strategy_roadmap():
    """Get latest strategy roadmap"""
    roadmap = strategy_service.get_latest_strategy_roadmap()
    
    if not roadmap:
        raise HTTPException(
            status_code=404,
            detail="No strategy roadmaps found"
        )
    
    return roadmap


@router.get("/strategy/latest/{objective}")
def get_latest_strategy_roadmap_by_objective(objective: str):
    """Get latest strategy roadmap for objective"""
    try:
        obj = OptimizationObjective(objective)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid objective: {objective}"
        )
    
    roadmap = strategy_service.get_latest_strategy_roadmap(obj)
    
    if not roadmap:
        raise HTTPException(
            status_code=404,
            detail=f"No strategy roadmap found for objective: {objective}"
        )
    
    return roadmap


@router.get("/strategy/all")
def get_all_strategy_roadmaps():
    """Get all strategy roadmaps"""
    roadmaps = strategy_service.get_all_strategy_roadmaps()
    
    if not roadmaps:
        raise HTTPException(
            status_code=404,
            detail="No strategy roadmaps found"
        )
    
    return {"roadmaps": roadmaps}
