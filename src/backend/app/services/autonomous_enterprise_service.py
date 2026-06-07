import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..models.autonomous_model import AutonomousCycleResult, AutonomousCycleHistory, AutonomousLoopMetrics
from ..models.self_optimization_model import OptimizationObjective
from ..models.multi_objective_model import ParetoFrontier
from .scenario_service import ScenarioService
from .self_optimization_service import SelfOptimizationService
from .strategy_service import StrategyService
from .culture_service import CultureService
from .external_environment_service_v2 import ExternalEnvironmentServiceV2
from .ceo_learning_service import CeoLearningService
from .enterprise_evolution_service import EnterpriseEvolutionService
from .company_history_service import CompanyHistoryService
from .strategy_application_engine import apply_strategy_roadmap_to_state, calculate_strategy_effectiveness
from .executive_agent_service import ExecutiveAgentService
from .corporate_intent_service import CorporateIntentService
from .multi_objective_service import MultiObjectiveService


class AutonomousEnterpriseService:
    """Service for executing autonomous enterprise cycles with Executive Agents decision-making"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "autonomous"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.scenario_service = ScenarioService()
        self.optimization_service = SelfOptimizationService()
        self.strategy_service = StrategyService()
        self.culture_service = CultureService()
        self.environment_service = ExternalEnvironmentServiceV2()
        self.ceo_service = CeoLearningService()
        self.evolution_service = EnterpriseEvolutionService()
        self.history_service = CompanyHistoryService()
        
        # Step AC: Executive Agents integration
        self.executive_agent_service = ExecutiveAgentService()
        self.intent_service = CorporateIntentService()
        self.multi_objective_service = MultiObjectiveService()
        
        self.cycles_file = self.data_dir / "cycles.json"
        self._cycle_counter = self._load_cycle_counter()
    
    def _load_cycle_counter(self) -> int:
        """Load the cycle counter from history"""
        try:
            if self.cycles_file.exists():
                with open(self.cycles_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cycles = data.get("cycles", [])
                    if cycles:
                        return max(c.get("cycle_id", 0) for c in cycles) + 1
            return 1
        except Exception:
            return 1
    
    def _save_cycle_result(self, result: AutonomousCycleResult):
        """Save cycle result to file"""
        try:
            history = self._load_cycle_history()
            history.cycles.append(result)
            history.total_cycles = len(history.cycles)
            
            # Calculate average evolution change
            if history.cycles:
                avg_change = sum(c.evolution_score_change for c in history.cycles) / len(history.cycles)
                history.average_evolution_score_change = avg_change
            
            # Count objective distribution
            history.objective_distribution = {}
            for cycle in history.cycles:
                obj = cycle.objective.value
                history.objective_distribution[obj] = history.objective_distribution.get(obj, 0) + 1
            
            # Track most applied strategies
            strategy_counts = {}
            for cycle in history.cycles:
                for strategy in cycle.applied_strategies:
                    strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            history.most_applied_strategies = sorted(
                strategy_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            with open(self.cycles_file, "w", encoding="utf-8") as f:
                json.dump(history.model_dump(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cycle result: {str(e)}")
    
    def _load_cycle_history(self) -> AutonomousCycleHistory:
        """Load cycle history from file"""
        try:
            if self.cycles_file.exists():
                with open(self.cycles_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return AutonomousCycleHistory(**data)
        except Exception:
            pass
        return AutonomousCycleHistory()
    
    def run_autonomous_cycle(self, objective: OptimizationObjective) -> Optional[AutonomousCycleResult]:
        """
        Execute one complete autonomous cycle with Executive Agents decision-making (Step AC):
        
        1. Get current state
        2. Run scenarios (Step U)
        3. Generate optimization plan (Step V)
        4. Generate Pareto frontier (Step AB)
        5. Executive Agents council decides strategy (Step AC - NEW)
        6. Apply strategies to state
        7. Update Intent from execution results (Step AA - Learning)
        8. Save new state
        9. Return results with executive decision
        """
        try:
            cycle_id = self._cycle_counter
            self._cycle_counter += 1
            
            # Step 1: Get current state
            latest_culture = self.culture_service.get_latest_culture()
            latest_environment = self.environment_service.get_environment(self._get_period())
            latest_evolution = self.evolution_service.get_latest_evolution_result()
            
            if not (latest_culture and latest_evolution):
                return None
            
            # Store previous state
            previous_evolution_score = latest_evolution.evolution_score
            previous_culture = {
                "innovation_culture": latest_culture.innovation_culture,
                "aggressiveness_culture": latest_culture.aggressiveness_culture,
                "stability_culture": latest_culture.stability_culture,
            }
            previous_environment = {
                "economic": latest_environment.pest.economic,
                "technological": latest_environment.pest.technological,
            }
            
            # Step 2: Run scenarios
            try:
                self.scenario_service.run_all_scenarios(latest_culture, latest_environment)
            except Exception as e:
                print(f"Scenario execution warning: {str(e)}")
            
            # Step 3: Generate optimization plan
            plan = self.optimization_service.generate_self_optimization_plan(objective)
            if not plan:
                return None
            
            # Step 4: Generate Pareto frontier (Multi-Objective)
            try:
                frontier = self.multi_objective_service.get_frontier()
            except Exception as e:
                print(f"Frontier generation warning: {str(e)}")
                frontier = None
            
            # Step AC: Executive Agents council decides strategy
            executive_decision = None
            selected_strategy_roadmap = None
            
            if frontier and frontier.candidates:
                try:
                    # Run executive council
                    executive_decision = self.executive_agent_service.run_executive_decision(
                        frontier=frontier
                    )
                    
                    # Find the selected roadmap by candidate ID
                    if executive_decision:
                        selected_id = executive_decision.selected_candidate_id
                        for candidate in frontier.candidates:
                            if candidate.id == selected_id or \
                               f"{candidate.scenario_type}_{candidate.optimization_objective}" == selected_id:
                                # Get roadmap for selected strategy
                                selected_strategy_roadmap = self.strategy_service.generate_strategy_roadmap(
                                    objective
                                )
                                break
                except Exception as e:
                    print(f"Executive decision warning: {str(e)}")
                    # Fall back to objective-based roadmap
                    selected_strategy_roadmap = self.strategy_service.generate_strategy_roadmap(objective)
            else:
                # No frontier available, use objective-based selection
                selected_strategy_roadmap = self.strategy_service.generate_strategy_roadmap(objective)
            
            if not selected_strategy_roadmap:
                return None
            
            # Step 5: Apply strategies to state
            new_culture, new_executive_team, new_environment, new_evolution, app_details = \
                apply_strategy_roadmap_to_state(
                    selected_strategy_roadmap,
                    latest_culture,
                    {role: self.ceo_service.get_latest_persona() for role in ["CEO"]},
                    latest_environment,
                    latest_evolution
                )
            
            # Step 6: Save new state
            try:
                new_culture.period = self._get_period()
            except Exception as e:
                print(f"State persistence warning: {str(e)}")
            
            # Calculate metrics
            new_evolution_score = new_evolution.evolution_score
            evolution_score_change = new_evolution_score - previous_evolution_score
            
            # Step 7: Update Intent from execution results (Learning)
            try:
                # Trigger Intent learning from this cycle
                self.intent_service.update_intent_from_learning()
            except Exception as e:
                print(f"Intent learning warning: {str(e)}")
            
            # Step 8: Create result with executive decision
            result = AutonomousCycleResult(
                cycle_id=cycle_id,
                timestamp=datetime.now().isoformat(),
                objective=objective,
                previous_evolution_score=previous_evolution_score,
                previous_culture_state=previous_culture,
                previous_environment_state=previous_environment,
                applied_strategies=[s.title for s in selected_strategy_roadmap.strategies],
                strategy_applications=app_details,
                executive_decision=executive_decision,  # Step AC: Add executive decision
                new_evolution_score=new_evolution_score,
                new_culture_state={
                    "innovation_culture": new_culture.innovation_culture,
                    "aggressiveness_culture": new_culture.aggressiveness_culture,
                    "stability_culture": new_culture.stability_culture,
                },
                new_environment_state={
                    "economic": new_environment.pest.economic,
                    "technological": new_environment.pest.technological,
                },
                evolution_score_change=evolution_score_change,
                cycle_summary=self._build_cycle_summary(
                    cycle_id,
                    objective,
                    selected_strategy_roadmap,
                    previous_evolution_score,
                    new_evolution_score,
                    evolution_score_change,
                    executive_decision
                ),
            )
            
            # Step 9: Save result
            self._save_cycle_result(result)
            
            return result
        except Exception as e:
            print(f"Error running autonomous cycle: {str(e)}")
            return None
    
    def _build_cycle_summary(
        self,
        cycle_id: int,
        objective,
        roadmap,
        prev_score: float,
        new_score: float,
        change: float,
        executive_decision
    ) -> str:
        """Build comprehensive cycle summary including executive decision"""
        summary = (
            f"Autonomous Cycle {cycle_id}: {objective.value}\n"
            f"Applied {len(roadmap.strategies)} strategies\n"
            f"Evolution: {prev_score:.2f} → {new_score:.2f} ({change:+.4f})"
        )
        
        if executive_decision:
            summary += (
                f"\nExecutive Decision: {executive_decision.selected_candidate_id}\n"
                f"Consensus Level: {len(executive_decision.supporting_roles)} "
                f"role(s) support, {len(executive_decision.opposing_roles)} oppose\n"
                f"Aggregated Score: {executive_decision.aggregated_score:.3f}"
            )
        
        return summary
    
    def get_cycle_history(self) -> Optional[AutonomousCycleHistory]:
        """Get all cycle history"""
        try:
            return self._load_cycle_history()
        except Exception:
            return None
    
    def get_latest_cycle(self) -> Optional[AutonomousCycleResult]:
        """Get latest cycle result"""
        try:
            history = self._load_cycle_history()
            if history.cycles:
                return history.cycles[-1]
        except Exception:
            pass
        return None
    
    def get_cycles_by_objective(self, objective: OptimizationObjective) -> list:
        """Get all cycles for specific objective"""
        try:
            history = self._load_cycle_history()
            return [c for c in history.cycles if c.objective == objective]
        except Exception:
            return []
    
    def get_autonomous_metrics(self) -> Optional[AutonomousLoopMetrics]:
        """Get aggregate metrics from all cycles"""
        try:
            history = self._load_cycle_history()
            if not history.cycles:
                return None
            
            cycles = history.cycles
            total_evolution_change = sum(c.evolution_score_change for c in cycles)
            
            # Calculate volatility
            changes = [c.evolution_score_change for c in cycles]
            mean_change = total_evolution_change / len(changes)
            variance = sum((c - mean_change) ** 2 for c in changes) / len(changes)
            volatility = variance ** 0.5
            
            # Find best objective
            obj_results = {}
            for obj in OptimizationObjective:
                obj_cycles = [c for c in cycles if c.objective == obj]
                if obj_cycles:
                    obj_results[obj.value] = sum(c.evolution_score_change for c in obj_cycles) / len(obj_cycles)
            
            best_obj = max(obj_results.items(), key=lambda x: x[1])[0] if obj_results else None
            
            # Strategy effectiveness
            strategy_effectiveness = {}
            for cycle in cycles:
                for strategy, details in cycle.strategy_applications.items():
                    if strategy not in strategy_effectiveness:
                        strategy_effectiveness[strategy] = {"total_impact": 0.0, "count": 0}
                    strategy_effectiveness[strategy]["total_impact"] += cycle.evolution_score_change
                    strategy_effectiveness[strategy]["count"] += 1
            
            avg_effectiveness = {
                k: v["total_impact"] / v["count"] if v["count"] > 0 else 0
                for k, v in strategy_effectiveness.items()
            }
            
            return AutonomousLoopMetrics(
                total_cycles_executed=len(cycles),
                average_cycle_duration_seconds=0.0,  # Could measure actual time
                total_evolution_score_change=total_evolution_change,
                evolution_score_volatility=volatility,
                objective_with_best_results=best_obj,
                strategy_effectiveness_map=avg_effectiveness,
            )
        except Exception:
            return None
    
    def _get_period(self) -> str:
        """Get current period in YYYY-MM format"""
        now = datetime.now()
        return f"{now.year}-{now.month:02d}"
