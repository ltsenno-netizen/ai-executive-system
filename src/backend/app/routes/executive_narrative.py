from fastapi import APIRouter, HTTPException, Query

from ..services.executive_narrative_service import ExecutiveNarrativeService

router = APIRouter()
service = ExecutiveNarrativeService()


@router.get('/narrative/monthly')
def get_monthly_narrative(month: int = Query(..., ge=1, le=12)):
    try:
        return service.generate_monthly_narrative(month)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/narrative/annual')
def get_annual_narrative(year: int = Query(..., ge=2020, le=2030)):
    try:
        return service.generate_annual_narrative(year)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/narrative/latest')
def get_latest_narrative():
    try:
        return service.get_latest_narrative().model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/narrative/{year}/{month}')
def get_narrative_by_period(year: int, month: int):
    try:
        if month < 1 or month > 12:
            raise ValueError('month must be between 1 and 12')
        period = f"{year:04d}-{month:02d}"
        return service.get_narrative(period).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/narrative/history')
def get_narrative_history(limit: int = Query(6, ge=1, le=12)):
    try:
        narratives = service.list_narratives(limit)
        return [item.model_dump() for item in narratives]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/narrative/multiyear')
def get_multi_year_narrative(
    start: int = Query(..., ge=2000, le=2030),
    end: int = Query(..., ge=2000, le=2030),
):
    try:
        return service.generate_multi_year_narrative(start, end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
