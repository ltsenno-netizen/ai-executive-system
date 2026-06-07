from fastapi import APIRouter, HTTPException
from enterprise_evolution_service import EnterpriseEvolutionService

router = APIRouter()
evolution_service = EnterpriseEvolutionService()


@router.get("/evolution/latest")
async def get_latest_evolution():
    result = evolution_service.get_latest_evolution_result()
    if not result:
        raise HTTPException(status_code=404, detail="No evolution data found")
    return result


@router.get("/evolution/{period}")
async def get_evolution_by_period(period: str):
    result = evolution_service.get_evolution_result(period)
    if not result:
        raise HTTPException(status_code=404, detail=f"No evolution data found for period {period}")
    return result