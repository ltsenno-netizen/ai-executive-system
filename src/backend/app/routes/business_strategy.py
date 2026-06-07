from fastapi import APIRouter, HTTPException
from ..services.business_strategy_service import BusinessStrategyService

router = APIRouter()

@router.get('/business/horipro/strategy')
def get_horipro_business_strategy():
    service = BusinessStrategyService()
    try:
        strategy = service.load_business_strategy()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return strategy.model_dump()
