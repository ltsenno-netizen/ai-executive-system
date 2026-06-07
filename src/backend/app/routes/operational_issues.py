from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from ..services.operational_issues_service import OperationalIssuesService
from ..models.operational_issues_model import IssueDefinition, IssueInstance, ImprovementAction

router = APIRouter()
service = OperationalIssuesService()


class MonthRequest(BaseModel):
    month: int


@router.get('/issues', response_model=List[IssueDefinition])
def get_issues():
    try:
        model = service.load_issues_model()
        return model.issues
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post('/issues/detect', response_model=List[IssueInstance])
def detect_issues(request: MonthRequest):
    try:
        monthly_state = service.integration_service.simulate_month_full(request.month)
        company_kpis = monthly_state.get('pl', {}).get('kpis', {})
        return service.detect_issues(monthly_state, company_kpis, request.month)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post('/issues/recommend', response_model=List[ImprovementAction])
def recommend_actions(request: MonthRequest):
    try:
        monthly_state = service.integration_service.simulate_month_full(request.month)
        company_kpis = monthly_state.get('pl', {}).get('kpis', {})
        issues = service.detect_issues(monthly_state, company_kpis, request.month)
        return service.generate_recommendations(issues)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post('/issues/simulate-month')
def simulate_month_with_issues(request: MonthRequest):
    try:
        return service.simulate_month_with_issues(request.month)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
