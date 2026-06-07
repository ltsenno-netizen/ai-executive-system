from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .scenario_model import ScenarioType
from .culture_model import CultureProfile
from .corporate_consciousness_evolution_model import ConsciousnessEvolutionState
from .external_environment_model_v2 import ExternalEnvironmentState


class ScenarioSimulationDefinition(BaseModel):
    scenario_type: ScenarioType
    description: str
    duration_months: int
    environment_modifiers: Dict[str, float]
    scenario_drivers: Dict[str, str] = Field(default_factory=dict)
    stress_factors: Dict[str, float] = Field(default_factory=dict)
    narrative_focus: Optional[str] = None
    confidence_adjustment: float = Field(default=0.0, ge=-0.5, le=0.5)


class ScenarioSimulationResult(BaseModel):
    scenario_type: ScenarioType
    description: str
    duration_months: int
    scenario_drivers: Dict[str, str]
    stress_factors: Dict[str, float]
    narrative_focus: Optional[str]
    projected_environment: ExternalEnvironmentState
    projected_culture: CultureProfile
    projected_consciousness_evolution: ConsciousnessEvolutionState
    financial_impact_summary: Dict[str, float]
    risk_assessment: str
    opportunity_assessment: str
    scenario_score: float
    confidence: float
    contingency_recommendations: List[str]
    strategic_implications: List[str]
    created_at: datetime = Field(default_factory=datetime.now)
