from typing import List, Optional
from pydantic import BaseModel, Field
from .scenario_model import ScenarioType
from .self_optimization_model import OptimizationObjective, SelfOptimizationPlan
from .strategy_model import StrategyRoadmap


class ObjectiveVector(BaseModel):
    """Multi-dimensional objective vector for Pareto optimization"""
    growth: float = Field(..., ge=0.0, description="Growth objective (normalized 0-100+)")
    profitability: float = Field(..., ge=0.0, description="Profitability objective (normalized 0-100+)")
    innovation: float = Field(..., ge=0.0, le=1.0, description="Innovation/Evolution score (0-1)")
    stability: float = Field(..., ge=0.0, le=1.0, description="Stability score (0-1), risk-normalized")

    class Config:
        json_schema_extra = {
            "example": {
                "growth": 130.0,
                "profitability": 13.0,
                "innovation": 0.75,
                "stability": 0.8
            }
        }


class StrategyCandidate(BaseModel):
    """Complete strategy option with multi-objective evaluation"""
    scenario_type: ScenarioType = Field(..., description="Underlying scenario")
    optimization_objective: Optional[OptimizationObjective] = Field(None, description="Primary optimization objective")
    scenario_summary: str = Field(..., description="Brief scenario description")
    objective_vector: ObjectiveVector = Field(..., description="Objective vector evaluation")
    roadmap_title: str = Field(..., description="Strategy roadmap title/summary")
    strategy_count: int = Field(..., ge=0, description="Number of strategies in roadmap")
    key_focus: str = Field(..., description="Primary strategic focus area")
    expected_risks: List[str] = Field(default_factory=list, description="Key risks for this path")
    expected_benefits: List[str] = Field(default_factory=list, description="Key benefits for this path")

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_type": "OPTIMISTIC",
                "optimization_objective": "GROWTH",
                "objective_vector": {
                    "growth": 130.0,
                    "profitability": 13.0,
                    "innovation": 0.75,
                    "stability": 0.8
                }
            }
        }


class ParetoDominanceInfo(BaseModel):
    """Information about dominance relationships"""
    candidate_index: int = Field(..., description="Index in candidates list")
    dominated_by: List[int] = Field(default_factory=list, description="Indices of candidates that dominate this one")
    dominates: List[int] = Field(default_factory=list, description="Indices this candidate dominates")
    is_pareto_optimal: bool = Field(..., description="Whether this candidate is on Pareto frontier")


class ParetoFrontier(BaseModel):
    """Complete Pareto frontier analysis results"""
    total_candidates: int = Field(..., ge=1, description="Total candidates evaluated")
    frontier_count: int = Field(..., ge=1, description="Number of Pareto-optimal candidates")
    candidates: List[StrategyCandidate] = Field(..., description="All evaluated candidates")
    frontier_indices: List[int] = Field(..., description="Indices of frontier candidates in candidates list")
    dominance_info: List[ParetoDominanceInfo] = Field(default_factory=list, description="Dominance relationships")
    
    # Frontier aggregates
    best_growth: float = Field(..., description="Maximum growth in frontier")
    best_profitability: float = Field(..., description="Maximum profitability in frontier")
    best_innovation: float = Field(..., description="Maximum innovation in frontier")
    best_stability: float = Field(..., description="Maximum stability in frontier")
    
    summary: str = Field(..., description="Summary of Pareto frontier analysis")

    class Config:
        json_schema_extra = {
            "example": {
                "total_candidates": 12,
                "frontier_count": 5,
                "frontier_indices": [0, 2, 5, 8, 11],
                "best_growth": 140.0,
                "best_profitability": 15.0,
                "best_innovation": 0.82,
                "best_stability": 0.85,
                "summary": "5 Pareto-optimal strategies identified from 12 candidates"
            }
        }
