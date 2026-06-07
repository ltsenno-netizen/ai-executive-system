from fastapi import APIRouter, HTTPException, Query
from typing import List
from ..services.corporate_fundamentals_service import CorporateFundamentalsService

router = APIRouter()
service = CorporateFundamentalsService()


@router.get('/fundamentals')
def get_corporate_fundamentals():
    try:
        model = service.load_fundamentals()
        return model.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/fundamentals/history')
def get_fundamentals_history():
    try:
        model = service.load_fundamentals()
        return [event.model_dump() for event in model.history]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/fundamentals/impact')
def get_monthly_fundamentals_impact(
    month: int = Query(..., ge=1, le=12, description='対象月'),
    year: int = Query(2026, ge=2026, description='対象年'),
):
    try:
        result = service.build_monthly_fundamentals_impact(month, year)
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
