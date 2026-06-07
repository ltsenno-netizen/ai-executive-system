from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from .self_optimization_model import OptimizationObjective
from .executive_agent_model import ExecutiveDecisionResult


class AutonomousCycleResult(BaseModel):
    """Result of a single autonomous cycle execution"""
    cycle_id: int = Field(..., description="Unique cycle identifier")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Cycle execution time")
    objective: OptimizationObjective = Field(..., description="Optimization objective for this cycle")
    
    # Input state
    previous_evolution_score: float = Field(..., ge=0.0, le=1.0, description="Evolution score before cycle")
    previous_culture_state: Dict[str, float] = Field(default_factory=dict, description="Culture state before cycle")
    previous_environment_state: Dict[str, float] = Field(default_factory=dict, description="Environment state before cycle")
    
    # Processing
    applied_strategies: List[str] = Field(default_factory=list, description="Strategies applied from roadmap")
    strategy_applications: Dict[str, Dict[str, float]] = Field(
        default_factory=dict, 
        description="Details of how each strategy was applied (impact on different dimensions)"
    )
    
    # Executive Decision (Step AB/AC)
    executive_decision: Optional[ExecutiveDecisionResult] = Field(
        default=None,
        description="Decision made by Executive Agents Council"
    )
    
    # Output state
    new_evolution_score: float = Field(..., ge=0.0, le=1.0, description="Evolution score after cycle")
    new_culture_state: Dict[str, float] = Field(default_factory=dict, description="Culture state after cycle")
    new_environment_state: Dict[str, float] = Field(default_factory=dict, description="Environment state after cycle")
    
    # Results
    evolution_score_change: float = Field(default=0.0, description="Change in evolution score")
    cycle_summary: str = Field(..., description="Summary of cycle results and impacts")
    notes: Optional[str] = Field(None, description="Additional notes about cycle execution")

    class Config:
        json_schema_extra = {
            "example": {
                "cycle_id": 1,
                "timestamp": "2026-04-25T10:30:00",
                "objective": "GROWTH",
                "previous_evolution_score": 0.65,
                "previous_culture_state": {"innovation_culture": 0.60, "aggressiveness_culture": 0.50},
                "applied_strategies": ["新規事業投資", "マーケティング予算増大"],
                "new_evolution_score": 0.72,
                "evolution_score_change": 0.07,
                "cycle_summary": "GROWTH objective achieved with 7% evolution score improvement through new business and marketing initiatives"
            }
        }


class AutonomousCycleHistory(BaseModel):
    """Collection of autonomous cycle results"""
    cycles: List[AutonomousCycleResult] = Field(default_factory=list, description="List of cycle results")
    total_cycles: int = Field(default=0, description="Total cycles executed")
    average_evolution_score_change: float = Field(default=0.0, description="Average evolution change per cycle")
    objective_distribution: Dict[str, int] = Field(default_factory=dict, description="Count of cycles per objective")
    most_applied_strategies: List[str] = Field(default_factory=list, description="Top applied strategies")


class AutonomousLoopMetrics(BaseModel):
    """Metrics for autonomous loop performance"""
    total_cycles_executed: int = Field(default=0, description="Total cycles run")
    average_cycle_duration_seconds: float = Field(default=0.0, description="Average execution time")
    total_evolution_score_change: float = Field(default=0.0, description="Total improvement in evolution score")
    evolution_score_volatility: float = Field(default=0.0, description="Standard deviation of changes")
    objective_with_best_results: Optional[str] = Field(None, description="Objective that produced best results")
    strategy_effectiveness_map: Dict[str, float] = Field(
        default_factory=dict, 
        description="Average impact per strategy type"
    )
