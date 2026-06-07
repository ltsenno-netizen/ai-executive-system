from fastapi import APIRouter, HTTPException
from ..services.business_strategy_service import BusinessStrategyService

router = APIRouter()
service = BusinessStrategyService()

@router.get("/business/horipro/definition")
async def get_business_strategy_definition():
    """
    事業定義・戦略課題・優先施策を返す
    """
    try:
        definition = service.load_business_strategy_definition()
        return definition
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")