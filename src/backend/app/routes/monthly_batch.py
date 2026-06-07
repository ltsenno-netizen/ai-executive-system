from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.monthly_batch_service import MonthlyBatchResult, MonthlyBatchService

router = APIRouter()
service = MonthlyBatchService()


class MonthlyBatchRequest(BaseModel):
    period: str


@router.post('/batch/monthly', response_model=MonthlyBatchResult)
def run_monthly_batch(request: MonthlyBatchRequest):
    try:
        return service.run_monthly_cycle(request.period)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
