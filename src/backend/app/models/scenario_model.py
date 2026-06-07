from enum import Enum
from typing import Dict, List
from pydantic import BaseModel
from .culture_model import CultureProfile
from .external_environment_model_v2 import ExternalEnvironmentState
from .ai_ceo_model import AICeoPersona
from .ai_ceo_model import AICeoPersona


class ScenarioType(str, Enum):
    BASELINE = "baseline"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    TECH_BOOM = "tech_boom"
    RECESSION = "recession"


class ScenarioDefinition(BaseModel):
    scenario_type: ScenarioType
    description: str
    duration_months: int
    environment_modifiers: Dict[str, float]  # economic, tech, competitor, etc.


class ScenarioResult(BaseModel):
    scenario_type: ScenarioType
    projected_culture: CultureProfile
    projected_executive_team: Dict[str, AICeoPersona]
    projected_financials: Dict[str, float]  # revenue, profit, cash
    projected_evolution_score: float
    risk_assessment: str
    opportunity_assessment: str
