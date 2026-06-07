from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class DepartmentMission(BaseModel):
    department: str
    mission_statement: str
    objectives: List[str]

class UnitDefinition(BaseModel):
    name: str
    headcount: int
    roles: List[str]

class TaskTemplate(BaseModel):
    id: str
    title: str
    description: str
    priority: str = Field(..., description="High/Medium/Low")
    required_roles: List[str]
    estimated_days: int
    kpis: List[str]

class IncidentScenario(BaseModel):
    id: str
    title: str
    description: str
    triggers: List[str]
    impact: str
    recommended_actions: List[str]
    severity: str = Field(..., description="Critical/High/Medium/Low")

class MemberProfile(BaseModel):
    id: str
    name: str
    role: str
    experience_years: int
    strengths: List[str]
    challenges: List[str]
    current_tasks: List[str]
    development_plan_id: Optional[str] = None

class UnitState(BaseModel):
    unit_name: str
    open_tasks: List[TaskTemplate]
    incidents: List[IncidentScenario]
    kpi_values: Dict[str, float]