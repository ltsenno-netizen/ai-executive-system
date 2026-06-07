from pydantic import BaseModel
from typing import Dict, List

class MonthlyPL(BaseModel):
    month: int
    revenue: Dict[str, float]
    cost: Dict[str, float]
    profit: float = 0.0
    profit_margin: float = 0.0
    cash_flow: float = 0.0

class SeasonalityFactor(BaseModel):
    month: int
    revenue_multiplier: Dict[str, float]
    cost_multiplier: Dict[str, float]

class InvestmentPlan(BaseModel):
    category: str
    amount: float
    start_month: int
    end_month: int
    expected_return_rate: float

class CompanyKPI(BaseModel):
    month: int
    gross_profit: float = 0.0
    operating_profit: float = 0.0
    cash_balance: float = 0.0
    license_ratio: float = 0.0
    digital_ratio: float = 0.0
    talent_ltv_index: float = 1.0

class CompanyOperatingModel(BaseModel):
    fiscal_year: int
    monthly_pl: List[MonthlyPL]
    seasonality: List[SeasonalityFactor]
    investments: List[InvestmentPlan]
    kpis: List[CompanyKPI]

class MonthlySimulationResult(BaseModel):
    month: int
    revenue: Dict[str, float]
    cost: Dict[str, float]
    profit: float
    profit_margin: float
    cash_flow: float
    cash_balance: float
    free_cash_flow: float
    kpis: Dict[str, float]
