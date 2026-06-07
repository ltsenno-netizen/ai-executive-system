from datetime import datetime
from fastapi import APIRouter, Body, HTTPException, Query
from typing import Dict
from ..services.external_data_service import ExternalDataService
from ..services.external_environment_service import ExternalEnvironmentService
from ..services.scenario_service import ScenarioService

router = APIRouter()
service = ExternalEnvironmentService()
external_data_service = ExternalDataService()
scenario_service = ScenarioService()


@router.get('/environment/state')
def get_environment_state(month: int = Query(..., ge=1, le=12), year: int = Query(2026, ge=2026)):
    try:
        return service.build_environment_state(month, year)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/environment/segments')
def get_segments():
    try:
        model = service.load_external_environment()
        return [segment.model_dump() for segment in model.segments]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/environment/trends')
def get_trends():
    try:
        model = service.load_external_environment()
        return [trend.model_dump() for trend in model.trends]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/environment/shocks')
def get_shocks():
    try:
        model = service.load_external_environment()
        return [shock.model_dump() for shock in model.shocks]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/market/segments')
def get_market_segments():
    try:
        model = service.load_external_environment()
        return [
            {
                'id': segment.id,
                'name': segment.name,
                'current_index': service._calculate_monthly_index(segment, datetime.utcnow().month, datetime.utcnow().year),
                'growth_rate': segment.growth_rate,
                'volatility': segment.volatility,
            }
            for segment in model.segments
        ]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post('/market/events')
def ingest_market_event(event: Dict[str, object]):
    try:
        injected = external_data_service.ingest_external_event(event)
        return {'status': 'ok', 'event': injected.model_dump()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post('/market/simulate')
def simulate_market_scenario(
    start_month: int = Query(..., ge=1, le=12),
    end_month: int = Query(..., ge=1, le=12),
    year: int = Query(2026, ge=2026),
    scenario: Dict[str, object] = Body(...),
):
    try:
        result = scenario_service.simulate_scenario(scenario, start_month, end_month, year)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/market/historical')
def get_market_historical(
    segment: str = Query(..., description='対象市場セグメント'),
    years: int = Query(3, ge=1, le=10, description='過去年数'),
):
    try:
        backfilled = external_data_service.backfill_historical_indices(years)
        return {
            'segment': segment,
            'history': backfilled.get(segment, {}),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
