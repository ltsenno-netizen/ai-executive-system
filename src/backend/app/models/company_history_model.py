from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from .culture_model import CultureProfile
from .external_environment_model_v2 import ExternalEnvironmentState


class LeadershipEvent(BaseModel):
    period: str
    event_type: Literal["ceo_succession", "executive_succession"]
    role: Optional[str] = None
    from_name: Optional[str] = None
    to_name: Optional[str] = None
    rationale: Optional[str] = None


class CultureSnapshot(BaseModel):
    period: str
    culture: CultureProfile


class EnvironmentSnapshot(BaseModel):
    period: str
    environment: ExternalEnvironmentState


class EvolutionSnapshot(BaseModel):
    period: str
    evolution_score: float
    environment_pressure: float


class AnnualReport(BaseModel):
    year: int
    revenue_total: float
    profit_total: float
    major_events: List[str] = Field(default_factory=list)
    culture_trends: Dict[str, float] = Field(default_factory=dict)
    evolution_trend: float
    summary_markdown_path: str


class CompanyHistory(BaseModel):
    leadership_events: List[LeadershipEvent] = Field(default_factory=list)
    annual_reports: List[AnnualReport] = Field(default_factory=list)