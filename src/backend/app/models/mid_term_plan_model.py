from pydantic import BaseModel
from typing import Dict, List, Optional


class MidTermFinancialPlan(BaseModel):
    years: List[int]
    revenue_targets: List[float]
    operating_profit_targets: List[float]
    capex_plan: List[float]


class MidTermOrgPlan(BaseModel):
    headcount_plan: Dict[int, int]
    key_capabilities: List[str]


class MidTermMarketPlan(BaseModel):
    focus_segments: List[str]
    growth_themes: List[str]


class MidTermRiskPlan(BaseModel):
    key_risks: List[str]
    mitigations: List[str]


class BoardComment(BaseModel):
    approval_status: str
    comment: str


class MidTermPlan(BaseModel):
    start_year: int
    end_year: int
    vision: str
    financial: MidTermFinancialPlan
    organization: MidTermOrgPlan
    market: MidTermMarketPlan
    risk: MidTermRiskPlan
    board_approved: bool
    board_comment: BoardComment


class MidTermPlanSummary(BaseModel):
    start_year: int
    end_year: int
    vision: str
    board_approved: bool
