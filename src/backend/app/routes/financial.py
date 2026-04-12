from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ..models.financial_model import InvestmentDecisionRecord, InvestmentRequest
from ..services.business_portfolio_service import BusinessPortfolioService
from ..services.financial_service import FinancialService
from ..services.company_operations_integration_service import CompanyOperationsIntegrationService

router = APIRouter()
service = FinancialService()

@router.get('/financials')
def get_financials():
    try:
        model = service.load_financials()
        return model.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/financials/investment-request')
def submit_investment_request(request: InvestmentRequest):
    try:
        financials = service.load_financials()
        portfolio_unit = None
        try:
            portfolio_state = service.portfolio_service.load_portfolio_state()
            portfolio_unit = next(
                (unit for unit in portfolio_state.portfolio_units if unit.business_unit_id == request.business_unit_id),
                None,
            )
        except Exception:
            portfolio_unit = None

        decision = service.evaluate_investment_request(
            request,
            financials,
            portfolio_unit=portfolio_unit,
            org_service=service.org_service,
        )
        service.add_pending_request(request)

        return {
            'investment_decision': decision.model_dump(),
            'status': 'pending',
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/financials/investment-decision')
def apply_investment_decision(decision: InvestmentDecisionRecord):
    try:
        financials = service.load_financials()
        pending_requests = service.load_pending_requests()
        business_unit_id = None
        for request in pending_requests:
            if request.id == decision.investment_request_id:
                business_unit_id = request.business_unit_id
                break

        updated_financials = service.apply_investment_decision(decision, financials, business_unit_id=business_unit_id)
        service.save_financials(updated_financials)

        if decision.decision in {'Approved', 'Partial', 'Rejected'} and decision.investment_request_id:
            remaining = [req for req in pending_requests if req.id != decision.investment_request_id]
            service.save_pending_requests(remaining)

        return {
            'financials': updated_financials.model_dump(),
            'decision': decision.model_dump(),
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get('/financials/simulate')
def simulate_financial_cycle(month: int = Query(..., ge=1, le=12)):
    try:
        integration_service = CompanyOperationsIntegrationService()
        monthly_state = integration_service.simulate_month_full(month)
        pl_data = monthly_state.get('pl', {})
        financials = service.load_financials()
        pending_requests = service.load_pending_requests()

        result = service.simulate_financial_cycle(
            month,
            pl_data,
            financials,
            pending_requests,
            portfolio_service=service.portfolio_service,
            org_service=service.org_service,
        )

        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get('/financials/emergency')
def get_emergency_measures():
    try:
        financials = service.load_financials()
        return {'measures': service.emergency_liquidity_measures(financials)}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get('/financials/emergency-playbook')
def get_emergency_playbook():
    try:
        financials = service.load_financials()
        return {
            'playbook': service.generate_emergency_playbook(financials),
            'alert_templates': service.build_emergency_alert_templates(financials),
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
