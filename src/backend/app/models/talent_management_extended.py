from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class DepartmentMission(BaseModel):
    department: str
    mission_statement: str
    objectives: List[str]
    primary_kpis: List[str]

class RoleDefinition(BaseModel):
    role: str
    responsibilities: List[str]
    required_skills: List[str]
    default_experience_years: int

class TaskTemplate(BaseModel):
    id: str
    name: str
    description: str
    category: str
    priority: str = "Medium"  # High/Medium/Low
    estimated_hours: int
    required_roles: List[str]
    kpis: Dict[str, float]  # KPI影響度
    pl_impact_template: Dict[str, float]  # PL影響テンプレート

class TaskInstance(BaseModel):
    id: str
    template_id: str
    title: str
    description: str
    priority: str = "Medium"  # High/Medium/Low
    required_roles: List[str]
    estimated_hours: int
    assigned_to: Optional[str] = None
    status: str = "Open"  # Open/InProgress/Blocked/Done
    created_at: datetime
    due_date: Optional[datetime] = None
    related_project: Optional[str] = None
    pl_impact: Optional[Dict[str, float]] = None  # 収益影響の簡易表現

class IncidentInstance(BaseModel):
    id: str
    scenario_id: str
    title: str
    severity: str
    occurred_at: datetime
    status: str
    impact_estimate: str
    escalated_to: Optional[str] = None

class ProcessDefinition(BaseModel):
    name: str
    steps: List[Dict[str, str]]  # step_name, owner_role, sla_hours
    inputs: List[str]
    outputs: List[str]

class RACIEntry(BaseModel):
    process_name: str
    role: str
    responsibility: str  # R/A/C/I