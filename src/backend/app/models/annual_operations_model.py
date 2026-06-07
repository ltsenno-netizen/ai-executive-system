from pydantic import BaseModel
from typing import Dict, List, Optional

class MonthlyOperation(BaseModel):
    month: int
    department_load: Dict[str, float]
    event_tags: List[str]
    base_tasks: Dict[str, int]
    incident_rate: float
    notes: Optional[str] = None

class AnnualOperationsModel(BaseModel):
    fiscal_year: int
    monthly_operations: List[MonthlyOperation]

class MonthlyOperationResult(BaseModel):
    month: int
    department_load: Dict[str, float]
    generated_tasks: List[Dict[str, object]]
    generated_incidents: List[Dict[str, object]]
