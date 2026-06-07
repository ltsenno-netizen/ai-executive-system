from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..services.execution_capacity_service import ExecutionCapacityService

router = APIRouter()
service = ExecutionCapacityService()


class ExecutionUpdateRequest(BaseModel):
    month: int
    projects_completed: int
    delays: int
    kpi_success_rate: float
    capacity: Optional[float] = None
    load: Optional[float] = None


@router.get('/execution/state')
def get_execution_state():
    try:
        return service.get_current_state()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post('/execution/update')
def update_execution_state(request: ExecutionUpdateRequest):
    try:
        return service.update_monthly_performance(
            month=request.month,
            projects_completed=request.projects_completed,
            delays=request.delays,
            kpi_success_rate=request.kpi_success_rate,
            capacity=request.capacity,
            load=request.load,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/execution/forecast')
def get_execution_forecast():
    try:
        return service.forecast_next_months()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
