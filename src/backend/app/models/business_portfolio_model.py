from pydantic import BaseModel
from typing import Dict, List, Optional


class BusinessPortfolioUnit(BaseModel):
    id: str
    business_unit_id: str
    revenue: float
    profit: float
    profit_margin: float
    growth_rate: float
    market_alignment: float
    competitive_pressure: float
    risk_score: float
    investment_need: float
    investment_return_rate: float
    strategic_fit: float


class InvestmentDecision(BaseModel):
    business_unit_id: str
    decision: str
    reason: str
    expected_impact: Dict[str, float]
    required_budget: float


class InvestmentRequest(BaseModel):
    id: str
    business_unit_id: str
    requested_amount: float
    expected_return_rate: float
    payback_period_months: int
    strategic_priority: int
    requested_by: Optional[str] = None
    requested_month: Optional[int] = None


class InvestmentDecisionRecord(BaseModel):
    id: str
    investment_request_id: str
    decision: str  # "Approved" / "Rejected" / "Deferred" / "Partial"
    approved_amount: float
    reason: str
    impact_on_cash: float
    applied_month: Optional[int] = None


class BusinessPortfolioState(BaseModel):
    month: int
    portfolio_units: List[BusinessPortfolioUnit]
    decisions: List[InvestmentDecision]
