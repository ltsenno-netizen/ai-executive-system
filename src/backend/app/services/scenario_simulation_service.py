import json
import os
from typing import Dict, List, Optional

from ..models.scenario_simulation_model import ScenarioSimulationResult
from .scenario_simulation_engine import ScenarioSimulationEngine
from .culture_service import CultureService
from .external_environment_service_v2 import ExternalEnvironmentServiceV2
from .financial_service import FinancialService
from .corporate_consciousness_evolution_service import CorporateConsciousnessEvolutionService


class ScenarioSimulationService:
    """Service layer for Future Scenario Simulation (Step AJ)."""

    def __init__(self):
        self.engine = ScenarioSimulationEngine()
        self.storage_dir = os.path.join(os.path.dirname(__file__), '../../../data/scenario_simulations')
        os.makedirs(self.storage_dir, exist_ok=True)

    def run_all_simulations(self) -> List[ScenarioSimulationResult]:
        current_culture = self._get_current_culture()
        current_environment = self._get_current_environment()
        current_evolution = self._get_current_evolution_state()
        current_financials = self._get_current_financials()

        simulation_definitions = self.engine.generate_simulation_definitions()
        results: List[ScenarioSimulationResult] = []

        for definition in simulation_definitions:
            result = self.engine.run_simulation(
                definition,
                current_culture,
                current_environment,
                current_evolution,
                current_financials,
            )
            results.append(result)
            self._save_simulation_result(result)

        return results

    def get_simulation_result(self, scenario_type: str) -> Optional[ScenarioSimulationResult]:
        file_path = os.path.join(self.storage_dir, f"{scenario_type}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ScenarioSimulationResult(**data)

    def get_all_simulation_results(self) -> List[ScenarioSimulationResult]:
        results: List[ScenarioSimulationResult] = []
        for file_name in os.listdir(self.storage_dir):
            if not file_name.endswith(".json"):
                continue
            file_path = os.path.join(self.storage_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            try:
                results.append(ScenarioSimulationResult(**data))
            except Exception:
                continue
        return sorted(results, key=lambda result: result.created_at, reverse=True)

    def get_latest_simulation_preview(self) -> Optional[Dict[str, object]]:
        results = self.get_all_simulation_results()
        if not results:
            return None

        latest = results[0]
        return {
            "scenario_type": latest.scenario_type.value,
            "description": latest.description,
            "risk_assessment": latest.risk_assessment,
            "opportunity_assessment": latest.opportunity_assessment,
            "confidence": latest.confidence,
            "financial_impact_summary": latest.financial_impact_summary,
            "strategic_implications": latest.strategic_implications,
            "contingency_recommendations": latest.contingency_recommendations,
            "key_impacts": {
                "financial": latest.financial_impact_summary,
                "risk_assessment": latest.risk_assessment,
                "opportunity_assessment": latest.opportunity_assessment,
            },
        }

    def _get_current_culture(self):
        try:
            culture_service = CultureService()
            return culture_service.get_latest_culture()
        except Exception:
            from ..models.culture_model import CultureProfile
            return CultureProfile(
                period="2026-01",
                innovation_culture=0.5,
                people_culture=0.5,
                execution_culture=0.5,
                aggressiveness_culture=0.5,
                risk_aversion_culture=0.5,
                brand_culture=0.5,
                cost_culture=0.5,
                stability_culture=0.5,
            )

    def _get_current_environment(self):
        try:
            env_service = ExternalEnvironmentServiceV2()
            environment = env_service.get_latest_environment()
            if environment is not None:
                return environment

            return env_service.get_environment("2026-01") or env_service.generate_and_store_environment("2026-01")
        except Exception:
            from ..models.external_environment_model_v2 import ExternalEnvironmentState, PESTFactors, CompetitorAction
            return ExternalEnvironmentState(
                period="2026-01",
                pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.5),
                competitors=[CompetitorAction(competitor_name="Competitor A", aggressiveness=0.5, market_share_shift=0.03)],
                shocks=[],
                market_growth_modifier=0.02,
                risk_modifier=0.0,
            )

    def _get_current_evolution_state(self):
        try:
            evolution_service = CorporateConsciousnessEvolutionService()
            return evolution_service.get_state()
        except Exception:
            from ..models.corporate_consciousness_evolution_model import ConsciousnessEvolutionState
            return ConsciousnessEvolutionState()

    def _get_current_financials(self) -> Dict[str, float]:
        try:
            financial_service = FinancialService()
            financials = financial_service.load_financials()
            return {
                "revenue": financials.free_cash_flow * 12,
                "profit": financials.free_cash_flow,
                "cash": financials.cash_reserves,
            }
        except Exception:
            return {"revenue": 1000000, "profit": 100000, "cash": 5000000}

    def _save_simulation_result(self, result: ScenarioSimulationResult):
        file_path = os.path.join(self.storage_dir, f"{result.scenario_type.value}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=2, ensure_ascii=False, default=str)
