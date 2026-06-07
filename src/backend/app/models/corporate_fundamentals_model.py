from pydantic import BaseModel
from typing import Dict, List, Optional, Union


class CompanyProfile(BaseModel):
    name: str
    mission: str
    vision: str
    values: List[str]
    brand_position: str
    competitive_advantages: List[str]
    management_style: str


class BusinessUnit(BaseModel):
    id: str
    name: str
    description: str
    revenue_model: Union[str, List[str]]
    cost_structure: Dict[str, float]
    kpis: Dict[str, float]
    linked_market_segments: List[str]
    risk_factors: List[str]


class CustomerSegment(BaseModel):
    id: str
    name: str
    description: str
    behavior_patterns: Dict[str, float]
    sensitivity: Dict[str, float]
    linked_business_units: List[str]


class OrganizationUnit(BaseModel):
    id: str
    name: str
    role: str
    headcount: int
    skill_profile: Dict[str, float]
    unit_kpis: Dict[str, float]
    culture_traits: List[str]


class FinancialFundamentals(BaseModel):
    fixed_costs: Dict[str, float]
    variable_costs: Dict[str, float]
    assets: Dict[str, float]
    liabilities: Dict[str, float]
    cash_reserves: float
    financial_health_indicators: Dict[str, float]
    short_term_debt: Optional[float] = None
    long_term_debt: Optional[float] = None
    interest_rate_short: Optional[float] = None
    interest_rate_long: Optional[float] = None
    monthly_revenue: Optional[float] = None
    monthly_operating_expenses: Optional[float] = None
    capex_plan: Optional[Dict[str, float]] = None
    committed_capex: Optional[float] = None
    available_credit_line: Optional[float] = None
    liquidity_buffer_months: Optional[float] = None
    minimum_cash_threshold: Optional[float] = None
    monthly_debt_service: Optional[float] = None
    free_cash_flow: Optional[float] = None
    investment_policy: Optional[Dict[str, float]] = None


class CorporateHistoryEvent(BaseModel):
    year: int
    title: str
    description: str
    impact_on_strategy: Dict[str, float]
    impact_on_organization: Dict[str, float]


class CorporateFundamentalsModel(BaseModel):
    profile: CompanyProfile
    business_units: List[BusinessUnit]
    customer_segments: List[CustomerSegment]
    organization_units: List[OrganizationUnit]
    financials: FinancialFundamentals
    history: List[CorporateHistoryEvent]
    annual_revenue_distribution: Optional[Dict[str, float]] = None
