from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.company_operating_service import CompanyOperatingService

router = APIRouter()
service = CompanyOperatingService()

class SimulateMonthRequest(BaseModel):
    month: int

@router.get('/company/state')
def get_company_state():
    try:
        model = service.prepare_company_model()
        return model.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get('/company/monthly-pl')
def get_company_monthly_pl():
    try:
        model = service.prepare_company_model()
        return [month.model_dump() for month in model.monthly_pl]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/company/simulate-month')
def simulate_company_month(request: SimulateMonthRequest):
    try:
        result = service.simulate_month(request.month)
        return result.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
