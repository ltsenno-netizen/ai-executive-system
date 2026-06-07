from fastapi import APIRouter, HTTPException
from typing import Optional
from src.backend.app.services.enterprise_evolution_service import EnterpriseEvolutionService
from src.backend.app.models.enterprise_evolution_model import EnterpriseEvolutionResult

router = APIRouter()
service = EnterpriseEvolutionService()

@router.get("/api/evolution/latest", response_model=Optional[EnterpriseEvolutionResult])
async def get_latest_evolution():
    """Get the latest enterprise evolution result."""
    try:
        return service.get_latest_evolution()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get latest evolution: {str(e)}")

@router.get("/api/evolution/{period}", response_model=Optional[EnterpriseEvolutionResult])
async def get_evolution_by_period(period: str):
    """Get enterprise evolution result for a specific period."""
    try:
        return service.get_evolution_by_period(period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evolution for period {period}: {str(e)}")

@router.post("/api/evolution/run", response_model=EnterpriseEvolutionResult)
async def run_evolution_cycle():
    """Run a new enterprise evolution cycle."""
    try:
        return service.run_and_save_evolution()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run evolution cycle: {str(e)}")