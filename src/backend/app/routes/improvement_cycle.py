from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List

from ..services.improvement_cycle_service import ImprovementCycleService
from ..models.improvement_cycle_model import (
    ContinuousImprovementState,
    ImprovementHistory,
)

router = APIRouter()
service = ImprovementCycleService()


class MonthRequest(BaseModel):
    month: int


@router.post('/improvement/simulate-cycle')
def simulate_cycle(request: MonthRequest):
    try:
        return service.simulate_month_cycle(request.month)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/improvement/history', response_model=List[ImprovementHistory])
def get_history():
    try:
        state = service.load_cycle_state()
        return state.executed_actions
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/improvement/priority', response_model=Dict[str, float])
def get_priority():
    try:
        state = service.load_cycle_state()
        return state.updated_priorities
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
