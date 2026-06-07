from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AutopilotCyclePhase(str, Enum):
    PERCEPTION = "PERCEPTION"
    EVALUATION = "EVALUATION"
    PREDICTION = "PREDICTION"
    COMPARISON = "COMPARISON"
    STRATEGY = "STRATEGY"
    EXECUTION = "EXECUTION"
    LEARNING = "LEARNING"


class AutopilotPhaseResult(BaseModel):
    phase: AutopilotCyclePhase
    summary: str
    details: Optional[Dict[str, object]] = None
    succeeded: bool = True


class AutopilotCycleResult(BaseModel):
    cycle_id: str = Field(..., description="Unique cycle identifier")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Cycle start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Cycle completion timestamp")
    phases: List[AutopilotPhaseResult] = Field(default_factory=list)
    overall_status: str = Field(default="PENDING", description="Cycle status")
    summary: Optional[str] = None
    key_actions: List[str] = Field(default_factory=list)
    experience_notes: Optional[str] = None
    cycle_metrics: Dict[str, object] = Field(default_factory=dict)


class AutopilotCycleHistory(BaseModel):
    cycles: List[AutopilotCycleResult] = Field(default_factory=list)
    last_run_at: Optional[datetime] = None
    total_cycles: int = 0


class AutopilotSummary(BaseModel):
    last_cycle_id: Optional[str]
    last_run_at: Optional[datetime]
    overall_status: Optional[str]
    latest_summary: Optional[str]
    recent_actions: List[str] = Field(default_factory=list)
    next_focus: List[str] = Field(default_factory=list)
    average_phase_success_rate: float = 0.0

