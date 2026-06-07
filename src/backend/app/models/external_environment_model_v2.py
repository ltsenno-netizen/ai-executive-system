from pydantic import BaseModel
from typing import List, Optional


class PESTFactors(BaseModel):
    political: float      # 0.0〜1.0
    economic: float
    social: float
    technological: float


class CompetitorAction(BaseModel):
    competitor_name: str
    aggressiveness: float  # 0〜1
    market_share_shift: float  # ±%
    notes: Optional[str] = None


class MarketShock(BaseModel):
    shock_type: str  # "recession", "currency", "trend_shift", etc.
    severity: float  # 0〜1
    duration_months: int
    description: str


class ExternalEnvironmentState(BaseModel):
    period: str
    pest: PESTFactors
    competitors: List[CompetitorAction]
    shocks: List[MarketShock]
    market_growth_modifier: float  # 全体の成長率補正
    risk_modifier: float           # CEO/Board のリスク評価に影響