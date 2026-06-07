from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .strategy_engine_v2_model import StrategyDirective


class ExecutiveRole(str, Enum):
    CEO = "CEO"
    CFO = "CFO"
    COO = "COO"
    CPO = "CPO"
    CMO = "CMO"
    CHRO = "CHRO"
    CSO = "CSO"


class ExecutiveStance(str, Enum):
    STRONGLY_SUPPORT = "STRONGLY_SUPPORT"
    SUPPORT = "SUPPORT"
    NEUTRAL = "NEUTRAL"
    CONCERNED = "CONCERNED"
    OPPOSE = "OPPOSE"


class ExecutiveComment(BaseModel):
    role: ExecutiveRole
    stance: ExecutiveStance
    key_points: List[str]
    risks: List[str]
    opportunities: List[str]
    suggested_changes: List[str]


class ExecutiveVote(BaseModel):
    role: ExecutiveRole
    stance: ExecutiveStance
    rationale: str


class ExecutiveSimulationInput(BaseModel):
    scenario_type: str
    strategy_bundle_id: Optional[str] = Field(None, description="Existing strategy bundle ID to reuse")
    focus_horizon: str = Field(..., description="SHORT / MID / LONG")


class StrategyBundle(BaseModel):
    directive_id: str = Field(..., description="Unique strategy bundle identifier")
    scenario_type: Optional[str] = Field(None, description="Scenario type used to create the bundle")
    executive_summary: Optional[str] = Field(None, description="Strategy bundle executive summary")
    directives: List[StrategyDirective] = Field(default_factory=list, description="Strategic directives in the bundle")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions implied by the bundle")
    context_notes: Optional[str] = Field(None, description="Additional context or observations")


class ExecutiveSimulationResult(BaseModel):
    simulation_id: str
    scenario_type: str
    strategy_bundle_id: str
    comments: List[ExecutiveComment]
    votes: List[ExecutiveVote]
    consensus_level: float
    approved: bool
    minority_reports: List[str]
    ceo_summary: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
