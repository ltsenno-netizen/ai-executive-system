from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ..services.executive_dashboard_service import ExecutiveDashboardService

router = APIRouter()
service = ExecutiveDashboardService()


@router.get('/executive/dashboard')
def get_executive_dashboard(month: int = Query(..., ge=1, le=12)):
    try:
        return service.build_dashboard(month)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/executive/month/{month}')
def get_executive_dashboard_month(month: int):
    try:
        return service.build_dashboard(month)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/executive/forecast')
def get_executive_forecast(month: int = Query(..., ge=1, le=11)):
    try:
        return service.forecast_next_month(month)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
