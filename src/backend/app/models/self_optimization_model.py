from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .scenario_model import ScenarioType


class OptimizationObjective(str, Enum):
    GROWTH = "growth"
    STABILITY = "stability"
    INNOVATION = "innovation"
    PROFITABILITY = "profitability"


class StrategyAdjustment(BaseModel):
    description: str
    priority: int = Field(..., ge=1, le=10, description="1 = highest priority")
    expected_impact: float = Field(..., ge=0.0, le=1.0, description="Expected impact 0.0-1.0")


class CultureAdjustment(BaseModel):
    dimension: str
    delta: float
    rationale: str


class LeadershipAdjustment(BaseModel):
    role: str
    suggested_change: str  # "keep", "replace", "develop"
    rationale: str


class SelfOptimizationPlan(BaseModel):
    objective: OptimizationObjective
    selected_scenario: ScenarioType
    recommended_strategies: List[StrategyAdjustment]
    recommended_culture_shifts: List[CultureAdjustment]
    recommended_leadership_changes: List[LeadershipAdjustment]
    expected_evolution_score: float
    notes: Optional[str] = None
