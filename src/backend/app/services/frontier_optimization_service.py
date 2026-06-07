"""
Frontier Optimization Service (Step AD)

Orchestrates the complete frontier optimization lifecycle:
1. Get current frontier
2. Analyze shape
3. Compute tradeoff gradients
4. Identify optimization opportunities
5. Generate recommendations
6. Execute optimization
"""

from typing import Optional, Dict, List
from pathlib import Path
import json
from datetime import datetime

from ..models.multi_objective_model import ParetoFrontier
from .multi_objective_service import MultiObjectiveService
from .corporate_intent_service import CorporateIntentService
from .executive_agent_service import ExecutiveAgentService

from .frontier_analysis_engine import (
    analyze_frontier_shape,
    FrontierShapeReport,
)
from .tradeoff_gradient import (
    compute_tradeoff_gradients,
    estimate_frontier_quality,
    extract_actionable_insights,
    FrontierGradientReport,
)
from .strategy_space_optimizer import (
    optimize_strategy_space,
    estimate_frontier_potential,
    generate_optimized_frontier,
    StrategySpaceOptimizationReport,
)


class FrontierOptimizationResult:
    """Results from frontier optimization cycle"""
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.shape_report: Optional[FrontierShapeReport] = None
        self.gradient_report: Optional[FrontierGradientReport] = None
        self.optimization_report: Optional[StrategySpaceOptimizationReport] = None
        self.frontier_quality_scores: Dict[str, float] = {}
        self.frontier_potential: Dict[str, float] = {}
        self.actionable_insights: List[str] = []
        self.recommendations: List[str] = []
        self.optimized_frontier: Optional[ParetoFrontier] = None


class FrontierOptimizationService:
    """
    Service for Pareto frontier optimization
    
    Integrates:
    - Step AA: Corporate Intent
    - Step AB: Executive Agents
    - Step AC: Autonomous Loop
    - Step AD: Frontier Optimization (THIS)
    """
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "frontier_optimization"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.multi_objective_service = MultiObjectiveService()
        self.intent_service = CorporateIntentService()
        self.agent_service = ExecutiveAgentService()
        
        self.optimization_history_file = self.data_dir / "optimization_history.json"
        self.shape_analysis_file = self.data_dir / "shape_analysis.json"
        self.gradient_analysis_file = self.data_dir / "gradient_analysis.json"
    
    def get_current_frontier(self) -> Optional[ParetoFrontier]:
        """Retrieve current Pareto frontier"""
        try:
            return self.multi_objective_service.get_frontier()
        except Exception as e:
            print(f"Error retrieving frontier: {e}")
            return None
    
    def run_frontier_optimization_cycle(self) -> FrontierOptimizationResult:
        """
        Execute complete frontier optimization cycle
        """
        result = FrontierOptimizationResult()
        
        # Step 1: Get current frontier
        frontier = self.get_current_frontier()
        if not frontier or not frontier.frontier_indices:
            print("No frontier available for optimization")
            return result
        
        # Step 2: Analyze frontier shape
        result.shape_report = analyze_frontier_shape(frontier)
        print(f"Shape analysis complete: {result.shape_report.frontier_count} frontier points")
        
        # Step 3: Compute tradeoff gradients
        result.gradient_report = compute_tradeoff_gradients(frontier)
        result.frontier_quality_scores = estimate_frontier_quality(result.gradient_report)
        result.actionable_insights = extract_actionable_insights(result.gradient_report)
        print(f"Gradient analysis complete: {result.gradient_report.total_gradients} gradients")
        
        # Step 4: Identify optimization opportunities
        result.optimization_report = optimize_strategy_space(
            frontier,
            result.shape_report,
            result.gradient_report
        )
        print(f"Optimization analysis complete: {len(result.optimization_report.identified_gaps)} gaps identified")
        
        # Step 5: Estimate frontier potential
        result.frontier_potential = estimate_frontier_potential(
            result.shape_report,
            result.gradient_report
        )
        
        # Step 6: Generate optimized frontier
        result.optimized_frontier = generate_optimized_frontier(
            frontier,
            result.optimization_report
        )
        
        # Step 7: Build recommendations
        self._build_recommendations(result)
        
        # Step 8: Save results
        self._save_optimization_results(result)
        
        return result
    
    def _build_recommendations(self, result: FrontierOptimizationResult) -> None:
        """Build actionable recommendations from analysis"""
        recommendations = []
        
        # From shape analysis
        recommendations.extend(result.shape_report.gaps_and_opportunities)
        
        # From gradient analysis
        recommendations.extend(result.actionable_insights)
        
        # From optimization analysis
        recommendations.extend(result.optimization_report.optimization_actions)
        
        # From frontier potential
        if result.frontier_potential.get("reconstruction_potential", 0) > 0.4:
            recommendations.append("Consider frontier reconstruction for improved convexity")
        
        if result.frontier_potential.get("density_potential", 0) > 0.5:
            recommendations.append("Generate new candidates in sparse regions to improve coverage")
        
        # Consensus from Executive Agents
        intent = self.intent_service.get_current_intent()
        if intent:
            if intent.growth_weight > 0.35:
                recommendations.append("High growth preference detected - optimize for growth-profitable tradeoffs")
            if intent.stability_weight > 0.35:
                recommendations.append("Stability focus detected - ensure frontier includes conservative strategies")
        
        result.recommendations = recommendations
    
    def _save_optimization_results(self, result: FrontierOptimizationResult) -> None:
        """Save optimization results to files"""
        try:
            # Save shape analysis
            if result.shape_report:
                shape_dict = {
                    "timestamp": result.timestamp.isoformat(),
                    "frontier_count": result.shape_report.frontier_count,
                    "convexity_ratio": result.shape_report.convexity.convexity_ratio,
                    "is_convex": result.shape_report.convexity.is_convex,
                    "clustering_coefficient": result.shape_report.density.clustering_coefficient,
                    "overall_density": result.shape_report.density.overall_density,
                    "shape_characteristics": result.shape_report.shape_characteristics,
                    "optimization_readiness": result.shape_report.optimization_readiness,
                    "extreme_points_count": len(result.shape_report.extreme_points),
                    "tradeoff_cliffs_count": len(result.shape_report.tradeoff_cliffs),
                }
                with open(self.shape_analysis_file, "w") as f:
                    json.dump(shape_dict, f, indent=2)
            
            # Save gradient analysis
            if result.gradient_report:
                gradient_dict = {
                    "timestamp": result.timestamp.isoformat(),
                    "total_gradients": result.gradient_report.total_gradients,
                    "key_gradients_count": len(result.gradient_report.key_gradients),
                    "neutral_pairs_count": len(result.gradient_report.neutral_pairs),
                    "frontier_quality": result.frontier_quality_scores,
                    "gradient_balance": result.frontier_quality_scores.get("gradient_balance", 0),
                    "objective_independence": result.frontier_quality_scores.get("objective_independence", 0),
                }
                if result.gradient_report.dominant_tradeoff:
                    gradient_dict["dominant_tradeoff"] = {
                        "from": result.gradient_report.dominant_tradeoff.from_objective,
                        "to": result.gradient_report.dominant_tradeoff.to_objective,
                        "magnitude": result.gradient_report.dominant_tradeoff.gradient_magnitude,
                    }
                with open(self.gradient_analysis_file, "w") as f:
                    json.dump(gradient_dict, f, indent=2)
            
            # Save optimization history
            history_entry = {
                "timestamp": result.timestamp.isoformat(),
                "shape_readiness": result.shape_report.optimization_readiness if result.shape_report else None,
                "frontier_potential": result.frontier_potential,
                "optimization_points": len(result.optimization_report.identified_gaps) if result.optimization_report else 0,
                "redundant_candidates": result.optimization_report.redundant_count if result.optimization_report else 0,
                "new_candidates_suggested": result.optimization_report.new_candidates_suggested if result.optimization_report else 0,
                "estimated_improvement": result.optimization_report.estimated_frontier_improvement if result.optimization_report else 0,
            }
            
            # Load history
            history = []
            if self.optimization_history_file.exists():
                try:
                    with open(self.optimization_history_file, "r") as f:
                        history = json.load(f)
                except Exception:
                    pass
            
            # Append and save
            history.append(history_entry)
            with open(self.optimization_history_file, "w") as f:
                json.dump(history[-10:], f, indent=2)  # Keep last 10
            
        except Exception as e:
            print(f"Error saving optimization results: {e}")
    
    def get_optimization_summary(self) -> Dict:
        """Get summary of latest optimization"""
        try:
            if self.optimization_history_file.exists():
                with open(self.optimization_history_file, "r") as f:
                    history = json.load(f)
                    if history:
                        return history[-1]
        except Exception:
            pass
        
        return {}
    
    def get_shape_analysis(self) -> Optional[Dict]:
        """Get latest shape analysis"""
        try:
            if self.shape_analysis_file.exists():
                with open(self.shape_analysis_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def get_gradient_analysis(self) -> Optional[Dict]:
        """Get latest gradient analysis"""
        try:
            if self.gradient_analysis_file.exists():
                with open(self.gradient_analysis_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def get_optimization_history(self, limit: int = 10) -> List[Dict]:
        """Get optimization history"""
        try:
            if self.optimization_history_file.exists():
                with open(self.optimization_history_file, "r") as f:
                    history = json.load(f)
                    return history[-limit:]
        except Exception:
            pass
        return []
    
    def should_optimize_frontier(self) -> bool:
        """
        Determine if frontier should be optimized
        
        Returns True if:
        - Low convexity
        - Low density
        - Many gaps identified
        """
        frontier = self.get_current_frontier()
        if not frontier:
            return False
        
        shape_report = analyze_frontier_shape(frontier)
        
        # Decision criteria
        should_optimize = (
            shape_report.convexity.convexity_ratio < 0.7 or
            shape_report.density.overall_density < 0.2 or
            len(shape_report.gaps_and_opportunities) > 2
        )
        
        return should_optimize
    
    def get_frontier_health_score(self) -> float:
        """
        Compute overall frontier health (0-1)
        
        Based on convexity, density, and coverage
        """
        frontier = self.get_current_frontier()
        if not frontier:
            return 0.0
        
        shape_report = analyze_frontier_shape(frontier)
        
        scores = []
        scores.append(shape_report.convexity.convexity_ratio)
        scores.append(shape_report.density.overall_density)
        scores.append(1.0 - len(shape_report.gaps_and_opportunities) * 0.2)
        
        health_score = sum(scores) / len(scores)
        return min(1.0, max(0.0, health_score))
