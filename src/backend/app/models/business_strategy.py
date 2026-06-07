from typing import List, Dict
from pydantic import BaseModel

class RevenueBreakdown(BaseModel):
    category: str
    ratio: float
    revenue: float
    gross_margin_rate: float
    gross_profit: float

class BusinessInsight(BaseModel):
    key_point: str
    detail: str

class SensitivityAnalysis(BaseModel):
    scenario: str
    impact: str

class StrategicPriority(BaseModel):
    priority: str
    actions: List[str]

class BusinessStrategyModel(BaseModel):
    revenue_breakdown: List[RevenueBreakdown]
    insights: List[BusinessInsight]
    sensitivity: List[SensitivityAnalysis]
    priorities: List[StrategicPriority]

class RevenueStreamMapping(BaseModel):
    revenue_stream: str
    main_department: str
    related_units: List[str]

class OrganizationalGap(BaseModel):
    issue: str
    risk: str
    affected_units: List[str]

class StrategicTask(BaseModel):
    title: str
    actions: List[str]
    kpi: List[str]

class Phase0Deliverable(BaseModel):
    path: str
    description: str
    owner: str

class BusinessStrategyDefinition(BaseModel):
    revenue_mapping: List[RevenueStreamMapping]
    gaps: List[OrganizationalGap]
    strategic_tasks: List[StrategicTask]
    deliverables: List[Phase0Deliverable]
    kpi_set: Dict[str, List[str]]

