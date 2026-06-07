from pydantic import BaseModel
from typing import List, Optional, Literal
from .board_member_model import BoardMemberOpinion


class QuarterlyFinancialSummary(BaseModel):
    quarter: str  # "2026-Q1"
    revenue_total: float
    operating_profit_total: float
    cash_end: float
    revenue_vs_plan: float
    profit_vs_plan: float


class QuarterlyExecutionSummary(BaseModel):
    initiatives_completed: int
    initiatives_delayed: int
    org_load_index: float  # 0〜1


class QuarterlyBoardReview(BaseModel):
    status: Literal["approved", "conditional", "rejected"]
    rationale: str
    conditions: Optional[str] = None
    member_opinions: List[BoardMemberOpinion] = []


class QuarterlyReview(BaseModel):
    quarter: str
    financial: QuarterlyFinancialSummary
    execution: QuarterlyExecutionSummary
    gap_analysis: str
    next_quarter_focus: List[str]
    board_review: QuarterlyBoardReview