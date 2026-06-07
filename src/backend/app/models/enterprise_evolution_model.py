from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class EnterpriseEvolutionResult(BaseModel):
    period: str
    evolution_score: float = Field(description="Overall enterprise evolution score (0-100)")
    culture_shift: Dict[str, float] = Field(description="Changes in culture dimensions")
    environment_shift: Dict[str, float] = Field(description="Changes in environment factors")
    leadership_shift: Dict[str, float] = Field(description="Changes in leadership characteristics")
    feedback_loops: Dict[str, List[str]] = Field(description="Active feedback loops identified")
    recommendations: List[str] = Field(description="Evolution recommendations")

class EnterpriseEvolutionSummary(BaseModel):
    latest_period: Optional[str] = None
    current_evolution_score: Optional[float] = None
    culture_trends: Dict[str, str] = Field(default_factory=dict, description="Culture evolution trends")
    environment_adaptation: Dict[str, str] = Field(default_factory=dict, description="Environment adaptation status")
    leadership_development: Dict[str, str] = Field(default_factory=dict, description="Leadership development trends")