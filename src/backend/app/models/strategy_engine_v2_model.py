from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .corporate_intent_model import CorporateIntent
from .scenario_model import ScenarioType


class StrategyDirective(BaseModel):
    directive_id: str = Field(..., description="Unique directive identifier")
    name: str = Field(..., description="Short title for the strategic directive")
    description: str = Field(..., description="Detailed description of the directive")
    priority: float = Field(..., ge=0.0, le=1.0, description="Priority score (0-1)")
    rationale: str = Field(..., description="Why this directive matters")
    directive_type: str = Field(..., description="Type of directive, e.g. growth, resilience, execution")


class StrategicAsset(BaseModel):
    asset_id: str = Field(..., description="Unique asset identifier")
    name: str = Field(..., description="Name of the capability or initiative")
    asset_type: str = Field(..., description="Type of strategic asset")
    description: str = Field(..., description="Description of the asset or initiative")
    priority: float = Field(..., ge=0.0, le=1.0, description="Priority level for execution")
    expected_impact: float = Field(..., ge=0.0, le=1.0, description="Expected impact score")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies or enabling conditions")


class StrategyEngineV2Report(BaseModel):
    report_id: str = Field(..., description="Unique report identifier")
    scenario_type: ScenarioType = Field(..., description="Scenario that drove the strategy report")
    scenario_description: str = Field(..., description="Description of the scenario")
    generated_at: datetime = Field(default_factory=datetime.now, description="When the strategy report was created")
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="Alignment between strategy and corporate intent")
    risk_resilience_score: float = Field(..., ge=0.0, le=1.0, description="Resilience of the strategy against the scenario")
    growth_commitment_score: float = Field(..., ge=0.0, le=1.0, description="Degree of growth commitment captured in the strategy")
    frontier_health_score: float = Field(..., ge=0.0, le=1.0, description="Current frontier health used for strategic calibration")
    consciousness_alignment_score: float = Field(..., ge=0.0, le=1.0, description="How well the strategy aligns with corporate consciousness")
    strategy_directives: List[StrategyDirective] = Field(default_factory=list, description="High-level directives for execution")
    strategic_assets: List[StrategicAsset] = Field(default_factory=list, description="Assets, initiatives, or capabilities to build")
    scenario_insights: List[str] = Field(default_factory=list, description="Key insights derived from the scenario")
    executive_summary: str = Field(..., description="Executive summary of the recommended strategy")
    recommended_actions: List[str] = Field(default_factory=list, description="Specific recommended actions")
    reference_scores: Dict[str, float] = Field(default_factory=dict, description="Reference values used to compute the strategy")
    context_notes: Optional[str] = Field(None, description="Additional context or observations")


class StrategyV2Summary(BaseModel):
    scenario_type: str = Field(..., description="Scenario type for the latest strategy report")
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="Alignment score with corporate intent")
    risk_resilience_score: float = Field(..., ge=0.0, le=1.0, description="Resilience score for the latest strategy")
    frontier_health_score: float = Field(..., ge=0.0, le=1.0, description="Frontier health score used for the report")
    recommended_actions: List[str] = Field(default_factory=list, description="Top recommended actions")
    top_directives: List[str] = Field(default_factory=list, description="Top 3 strategic directives")
    executive_summary: str = Field(..., description="Executive summary of the latest strategy")
    generated_at: datetime = Field(default_factory=datetime.now, description="Creation time of the latest report")
