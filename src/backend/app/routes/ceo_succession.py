from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.ceo_succession_service import CeoSuccessionService
from ..models.ceo_succession_model import CeoSuccessionDecision

router = APIRouter()
service = CeoSuccessionService()


class CeoSuccessionRequest(BaseModel):
    period: str
    current_financials: dict = {}
    market_state: dict = {}
    org_state: dict = {}


@router.post('/ceo-succession', response_model=CeoSuccessionDecision)
def run_ceo_succession(request: CeoSuccessionRequest):
    try:
        return service.run_ceo_succession(
            request.period,
            current_financials=request.current_financials,
            market_state=request.market_state,
            org_state=request.org_state,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/ceo-succession/latest', response_model=CeoSuccessionDecision)
def get_latest_ceo_succession():
    decision = service.get_latest_succession_decision()
    if not decision:
        raise HTTPException(status_code=404, detail='No CEO succession decision found')
    return decision
