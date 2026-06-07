from pydantic import BaseModel
from typing import Optional
from .ai_ceo_model import AICeoPersona


class FinancialResultSummary(BaseModel):
    revenue: float
    operating_profit: float
    cash_flow: Optional[float] = None
    investment_recovery: Optional[float] = None


class CeoLearningSnapshot(BaseModel):
    period: str
    ceo_persona: AICeoPersona
    financial_result: FinancialResultSummary
    board_status: str  # approved / conditional / rejected
    notes: Optional[str] = None