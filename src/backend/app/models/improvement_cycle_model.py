from pydantic import BaseModel
from typing import Dict, List


class ImprovementHistory(BaseModel):
    id: str
    month: int
    issue_id: str
    action_id: str
    expected_effect: Dict[str, float]
    actual_effect: Dict[str, float]
    effect_error: Dict[str, float]
    priority_score: float


class ActionEffectiveness(BaseModel):
    action_id: str
    total_runs: int
    avg_effect: Dict[str, float]
    avg_error: Dict[str, float]
    updated_priority: float


class ContinuousImprovementState(BaseModel):
    month: int
    executed_actions: List[ImprovementHistory]
    updated_priorities: Dict[str, float]
    action_effectiveness: List[ActionEffectiveness] = []
