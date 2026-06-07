from fastapi import APIRouter, HTTPException, Query
from ..services.business_portfolio_service import BusinessPortfolioService

router = APIRouter()
service = BusinessPortfolioService()

@router.get('/portfolio')
def get_portfolio(month: int = Query(..., ge=1, le=12)):
    try:
        state = service.simulate_portfolio_cycle(month)
        return state.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get('/portfolio/decisions')
def get_portfolio_decisions(month: int = Query(..., ge=1, le=12)):
    try:
        state = service.simulate_portfolio_cycle(month)
        return [decision.model_dump() for decision in state.decisions]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get('/portfolio/units')
def get_portfolio_units(month: int = Query(..., ge=1, le=12)):
    try:
        state = service.simulate_portfolio_cycle(month)
        return [unit.model_dump() for unit in state.portfolio_units]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
