from pydantic import BaseModel
from typing import Dict, List


class OrganizationUnit(BaseModel):
    id: str
    name: str
    role: str
    headcount: int
    fte_capacity: float
    skill_profile: Dict[str, float]
    workload_index: float
    attrition_rate: float
    time_to_hire_months: float
    culture_traits: List[str]
    dependency_links: List[str]
    critical_roles: List[str]
    automation_index: float
    monthly_cost_per_fte: float


class OpenPosition(BaseModel):
    unit_id: str
    role: str
    posted_month: int


class OrganizationState(BaseModel):
    month: int
    units: List[OrganizationUnit]
    open_positions: List[OpenPosition]
