from typing import Dict, List, Optional
from pydantic import BaseModel


class ExecutionHistoryRecord(BaseModel):
    month: int
    projects_completed: int
    delays: int
    kpi_success_rate: float


class ExecutionState(BaseModel):
    capacity: float
    load: float
    efficiency: float
    history: List[ExecutionHistoryRecord] = []


class ExecutionRequirement(BaseModel):
    investment_request_id: str
    required_capacity: float
    duration_months: int
