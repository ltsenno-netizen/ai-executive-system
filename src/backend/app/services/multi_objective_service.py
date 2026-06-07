import json
from pathlib import Path
from typing import Optional

from ..models.multi_objective_model import (
    StrategyCandidate,
    ParetoFrontier,
)
from ..models.scenario_model import ScenarioType
from .scenario_service import ScenarioService
from .self_optimization_service import SelfOptimizationService
from .strategy_service import StrategyService
from .multi_objective_engine import (
    compute_objective_vector,
    build_pareto_frontier,
    identify_tradeoffs,
)


class MultiObjectiveService:
    """Service for multi-objective optimization and Pareto frontier analysis"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "multi_objective"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.scenario_service = ScenarioService()
        self.optimization_service = SelfOptimizationService()
        self.strategy_service = StrategyService()
        
        self.frontier_file = self.data_dir / "frontier.json"
    
    def generate_multi_objective_analysis(self) -> Optional[ParetoFrontier]:
        """
        Generate complete multi-objective analysis by:
        1. Getting all scenario results
        2. For each scenario, generating optimization plans for all objectives
        3. Computing objective vectors for each combination
        4. Building Pareto frontier
        5. Saving and returning results
        """
        try:
            candidates = []
            
            # Get all scenarios (or use cached latest)
            try:
                all_scenarios = self.scenario_service.get_all_scenario_results()
            except Exception:
                all_scenarios = {}
            
            # For each scenario, generate optimization plans and strategies
            for scenario_type_str, scenario_result in all_scenarios.items():
                try:
                    scenario_type = ScenarioType(scenario_type_str)
                except (ValueError, KeyError):
                    continue
                
                if not scenario_result:
                    continue
                
                # Try each optimization objective for this scenario
                optimization_objectives = [
                    "GROWTH", "PROFITABILITY", "INNOVATION", "STABILITY"
                ]
                
                for obj_str in optimization_objectives:
                    try:
                        # Generate optimization plan
                        from ..models.self_optimization_model import OptimizationObjective
                        obj = OptimizationObjective(obj_str)
                        
                        # Get or generate plan
                        plan = self.optimization_service.get_latest_plan(obj)
                        if not plan:
                            plan = self.optimization_service.generate_self_optimization_plan(obj)
                        
                        if not plan:
                            continue
                        
                        # Get or generate roadmap
                        roadmap = self.strategy_service.get_latest_strategy_roadmap(obj)
                        if not roadmap:
                            roadmap = self.strategy_service.generate_strategy_roadmap(obj)
                        
                        if not roadmap:
                            continue
                        
                        # Compute objective vector
                        obj_vector = compute_objective_vector(scenario_result, plan)
                        
                        # Create candidate
                        candidate = StrategyCandidate(
                            scenario_type=scenario_type,
                            optimization_objective=obj,
                            scenario_summary=f"{scenario_type.value} scenario with {obj.value} focus",
                            objective_vector=obj_vector,
                            roadmap_title=roadmap.key_focus,
                            strategy_count=len(roadmap.strategies),
                            key_focus=roadmap.key_focus,
                            expected_risks=[s.title for s in roadmap.strategies 
                                          if s.risk_level.value == "high"][:3],
                            expected_benefits=[s.title for s in roadmap.strategies 
                                             if s.expected_impact >= 0.7][:3],
                        )
                        
                        candidates.append(candidate)
                    except Exception as e:
                        print(f"Error processing {scenario_type_str} + {obj_str}: {str(e)}")
                        continue
            
            if not candidates:
                print("No valid candidates generated for multi-objective analysis")
                return None
            
            # Build Pareto frontier
            frontier = build_pareto_frontier(candidates)
            
            # Analyze tradeoffs
            tradeoffs = identify_tradeoffs(frontier)
            frontier.summary += f"\n\nTradeoff Analysis: {tradeoffs.get('interpretation', '')}"
            
            # Save to file
            self._save_frontier(frontier)
            
            return frontier
        except Exception as e:
            print(f"Error generating multi-objective analysis: {str(e)}")
            return None
    
    def _save_frontier(self, frontier: ParetoFrontier):
        """Save frontier to JSON file"""
        try:
            with open(self.frontier_file, "w", encoding="utf-8") as f:
                json.dump(frontier.model_dump(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving frontier: {str(e)}")
    
    def get_frontier(self) -> Optional[ParetoFrontier]:
        """Get latest Pareto frontier"""
        try:
            if self.frontier_file.exists():
                with open(self.frontier_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return ParetoFrontier(**data)
        except Exception as e:
            print(f"Error loading frontier: {str(e)}")
        return None
    
    def get_candidates(self) -> list:
        """Get all candidates from latest frontier"""
        frontier = self.get_frontier()
        if frontier:
            return frontier.candidates
        return []
    
    def get_frontier_candidates(self) -> list:
        """Get only Pareto-optimal candidates"""
        frontier = self.get_frontier()
        if frontier:
            return [frontier.candidates[i] for i in frontier.frontier_indices]
        return []
