from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.midterm_strategy_service import MidtermStrategyService
from ..services.mid_term_plan_service import MidTermPlanService

router = APIRouter()
service = MidtermStrategyService()
plan_service = MidTermPlanService()

class CurrentKPIsRequest(BaseModel):
    current_kpis: dict

class SimulateYearRequest(BaseModel):
    year: int

@router.get('/strategy/midterm')
def get_midterm_strategy():
    try:
        model = service.load_strategy_model()
        return model.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/strategy/gap-analysis')
def post_gap_analysis(request: CurrentKPIsRequest):
    try:
        strategy_model = service.load_strategy_model()
        gaps = service.evaluate_kpi_gap(request.current_kpis, strategy_model)
        return [gap.model_dump() for gap in gaps]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/strategy/recommend')
def post_recommend(request: CurrentKPIsRequest):
    try:
        strategy_model = service.load_strategy_model()
        gaps = service.evaluate_kpi_gap(request.current_kpis, strategy_model)
        recommendations = service.recommend_initiatives(gaps, strategy_model)
        return [rec.model_dump() for rec in recommendations]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/plans/midterm/generate')
def generate_midterm_plan(start_year: int = 2026, horizon_years: int = 3):
    try:
        plan = plan_service.generate_and_store_mid_term_plan(start_year=start_year, horizon_years=horizon_years)
        return plan.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get('/plans/midterm/latest')
def get_latest_midterm_plan():
    try:
        plan = plan_service.get_latest_plan()
        if plan is None:
            raise FileNotFoundError('No mid-term plan available')
        return plan.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get('/plans/midterm/{period}')
def get_midterm_plan_by_period(period: str):
    try:
        plan = plan_service.get_plan_by_period(period)
        return plan.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/strategy/simulate-year')
def simulate_year(request: SimulateYearRequest):
    try:
        result = service.simulate_year_with_strategy(request.year)
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
