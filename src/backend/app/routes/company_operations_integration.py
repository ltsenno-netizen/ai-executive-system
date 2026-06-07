from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.company_operations_integration_service import CompanyOperationsIntegrationService

router = APIRouter()
service = CompanyOperationsIntegrationService()

class SimulateMonthFullRequest(BaseModel):
    month: int

@router.post('/company/simulate-month-full')
def simulate_month_full(request: SimulateMonthFullRequest):
    try:
        result = service.simulate_month_full(request.month)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
