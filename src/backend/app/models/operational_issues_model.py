from pydantic import BaseModel
from typing import Dict, List, Optional


class IssueDefinition(BaseModel):
    id: str
    name: str
    description: str
    detection_rules: Dict[str, float]
    severity: str
    related_departments: List[str]


class IssueInstance(BaseModel):
    id: str
    issue_id: str
    month: int
    detected_values: Dict[str, float]
    severity: str
    status: str
    recommended_actions: List[str] = []


class ImprovementAction(BaseModel):
    id: str
    issue_id: str
    name: str
    description: str
    owner_department: str
    expected_effect: Dict[str, float]
    task_template_id: Optional[str] = None


class OperationalIssuesModel(BaseModel):
    issues: List[IssueDefinition]
    actions: List[ImprovementAction]
