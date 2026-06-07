from pydantic import BaseModel
from typing import Dict, List

class StrategyTheme(BaseModel):
    id: str
    name: str
    description: str
    target_kpis: Dict[str, float]

class AnnualStrategicGoal(BaseModel):
    fiscal_year: int
    theme_id: str
    target_value: float
    description: str

class StrategicInitiative(BaseModel):
    id: str
    theme_id: str
    name: str
    description: str
    expected_impact: Dict[str, float]
    investment_required: float
    owner_department: str

class StrategyGap(BaseModel):
    kpi_name: str
    current_value: float
    target_value: float
    gap: float
    severity: str

class StrategyRecommendation(BaseModel):
    theme_id: str
    initiative_id: str
    reason: str
    expected_effect: Dict[str, float]

class MidtermStrategyModel(BaseModel):
    themes: List[StrategyTheme]
    annual_goals: List[AnnualStrategicGoal]
    initiatives: List[StrategicInitiative]
