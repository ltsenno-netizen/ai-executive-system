from pydantic import BaseModel
from typing import Dict, List, Optional


class MarketSegment(BaseModel):
    id: str
    name: str
    description: str
    base_size: Optional[float] = None
    monthly_index: Optional[Dict[str, float]] = None
    seasonality: Optional[Dict[int, float]] = None
    growth_rate: Optional[float] = 0.0
    volatility: Optional[float] = 0.0
    shock_sensitivity: Optional[float] = 0.0
    external_indicators: Optional[Dict[str, float]] = None
    last_updated: Optional[str] = None


class IndustryTrend(BaseModel):
    id: str
    name: str
    description: str
    impact_on_segments: Dict[str, float]


class Competitor(BaseModel):
    id: str
    name: str
    description: str
    strength_by_segment: Dict[str, float]
    aggressiveness: float


class ExternalShock(BaseModel):
    id: str
    name: str
    description: str
    affected_segments: Dict[str, float]
    duration_months: int


class ExternalEvent(BaseModel):
    id: str
    date: str
    type: str
    impact_map: Dict[str, float]
    duration_months: int
    source: str
    notes: str


class ExternalEnvironmentModel(BaseModel):
    segments: List[MarketSegment]
    trends: List[IndustryTrend]
    competitors: List[Competitor]
    shocks: List[ExternalShock]
    external_events: Optional[List[ExternalEvent]] = None
