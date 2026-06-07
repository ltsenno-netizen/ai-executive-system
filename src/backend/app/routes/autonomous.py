from fastapi import APIRouter, HTTPException
from ..models.self_optimization_model import OptimizationObjective
from ..services.autonomous_enterprise_service import AutonomousEnterpriseService

router = APIRouter(tags=["autonomous"])
autonomous_service = AutonomousEnterpriseService()


@router.post("/autonomous/run/{objective}")
def run_autonomous_cycle(objective: str):
    """Run one complete autonomous cycle"""
    try:
        obj = OptimizationObjective(objective)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid objective: {objective}"
        )
    
    result = autonomous_service.run_autonomous_cycle(obj)
    
    if not result:
        raise HTTPException(
            status_code=500,
            detail="Failed to execute autonomous cycle"
        )
    
    return {
        "message": f"Completed autonomous cycle {result.cycle_id} with objective {objective}",
        "cycle": result
    }


@router.get("/autonomous/latest")
def get_latest_cycle():
    """Get latest cycle result"""
    cycle = autonomous_service.get_latest_cycle()
    
    if not cycle:
        raise HTTPException(
            status_code=404,
            detail="No cycles executed yet"
        )
    
    return cycle


@router.get("/autonomous/cycles")
def get_all_cycles():
    """Get all cycle history"""
    history = autonomous_service.get_cycle_history()
    
    if not history or not history.cycles:
        raise HTTPException(
            status_code=404,
            detail="No cycles executed yet"
        )
    
    return history


@router.get("/autonomous/cycles/{objective}")
def get_cycles_by_objective(objective: str):
    """Get all cycles for specific objective"""
    try:
        obj = OptimizationObjective(objective)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid objective: {objective}"
        )
    
    cycles = autonomous_service.get_cycles_by_objective(obj)
    
    if not cycles:
        raise HTTPException(
            status_code=404,
            detail=f"No cycles found for objective: {objective}"
        )
    
    return {
        "objective": objective,
        "cycles": cycles,
        "total_count": len(cycles)
    }


@router.get("/autonomous/metrics")
def get_autonomous_metrics():
    """Get autonomous loop performance metrics"""
    metrics = autonomous_service.get_autonomous_metrics()
    
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail="No metrics available - no cycles executed yet"
        )
    
    return metrics
