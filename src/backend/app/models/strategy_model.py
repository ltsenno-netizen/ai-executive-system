from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from .self_optimization_model import OptimizationObjective
from .scenario_model import ScenarioType


class StrategyHorizon(str, Enum):
    """Strategy execution horizon classification"""
    SHORT_TERM = "short_term"   # 0-12 months
    MID_TERM = "mid_term"       # 1-3 years
    LONG_TERM = "long_term"     # 3+ years


class StrategyRiskLevel(str, Enum):
    """Risk level for strategy execution"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StrategyItem(BaseModel):
    """Individual strategic action item"""
    title: str = Field(..., description="Strategy title")
    description: str = Field(..., description="Detailed description of strategy")
    horizon: StrategyHorizon = Field(..., description="Execution timeframe")
    priority: int = Field(..., ge=1, le=10, description="Priority level 1-10")
    expected_impact: float = Field(..., ge=0.0, le=1.0, description="Expected impact 0.0-1.0")
    risk_level: StrategyRiskLevel = Field(..., description="Execution risk level")
    dependencies: List[str] = Field(default_factory=list, description="Dependent strategies")


class StrategyRoadmap(BaseModel):
    """Complete strategy roadmap with prioritized actions"""
    objective: OptimizationObjective = Field(..., description="Optimization objective")
    selected_scenario: ScenarioType = Field(..., description="Selected scenario type")
    key_focus: str = Field(..., description="Primary strategic focus area")
    strategies: List[StrategyItem] = Field(..., description="Prioritized strategy items")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "objective": "GROWTH",
                "selected_scenario": "OPTIMISTIC",
                "key_focus": "成長ドライバーの最大化と新規市場開拓",
                "strategies": [
                    {
                        "title": "新規事業投資",
                        "description": "テック企業との協業で新規事業化",
                        "horizon": "mid_term",
                        "priority": 1,
                        "expected_impact": 0.8,
                        "risk_level": "medium",
                        "dependencies": []
                    }
                ],
                "notes": "Generated from optimization plan"
            }
        }
