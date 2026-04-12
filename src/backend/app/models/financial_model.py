from typing import Dict, List, Optional
from pydantic import BaseModel


class FinancialFundamentals(BaseModel):
    cash_reserves: float
    short_term_debt: float
    long_term_debt: float
    interest_rate_short: float
    interest_rate_long: float
    monthly_revenue: float
    monthly_operating_expenses: float
    capex_plan: Dict[str, float]
    committed_capex: float
    available_credit_line: float
    liquidity_buffer_months: float
    minimum_cash_threshold: float
    monthly_debt_service: float
    free_cash_flow: float
    investment_policy: Dict[str, float]
    financial_health_indicators: Dict[str, float]


class InvestmentRequest(BaseModel):
    id: str
    business_unit_id: str
    requested_amount: float
    expected_return_rate: float
    payback_period_months: int
    strategic_priority: int
    requested_by: Optional[str] = None
    requested_month: Optional[int] = None
    tranche_count: Optional[int] = None
    tranche_interval_months: Optional[int] = None


class InvestmentDecisionRecord(BaseModel):
    id: str
    investment_request_id: str
    decision: str  # "Approved" / "Rejected" / "Deferred" / "Partial"
    approved_amount: float
    partial_candidate: Optional[float] = None
    tranche_schedule: Optional[List[Dict[str, object]]] = None
    tranche_index: Optional[int] = None
    reason: str
    impact_on_cash: float
    applied_month: Optional[int] = None
