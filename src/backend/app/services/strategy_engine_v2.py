import random
from typing import Dict, List, Optional
from uuid import uuid4

from .corporate_intent_service import CorporateIntentService
from .scenario_simulation_service import ScenarioSimulationService
from .corporate_consciousness_service import CorporateConsciousnessService
from .frontier_optimization_service import FrontierOptimizationService
from ..models.strategy_engine_v2_model import (
    StrategyDirective,
    StrategicAsset,
    StrategyEngineV2Report,
)
from ..models.corporate_intent_model import CorporateIntent
from ..models.scenario_simulation_model import ScenarioSimulationResult
from ..models.corporate_consciousness_model import ConsciousnessDashboardSummary


class StrategyEngineV2:
    """Engine for integrated corporate strategy generation."""

    def __init__(self):
        self.intent_service = CorporateIntentService()
        self.frontier_service = FrontierOptimizationService()
        self.consciousness_service = CorporateConsciousnessService()
        self.scenario_service = ScenarioSimulationService()

    def generate_strategy_report(
        self,
        simulation_result: ScenarioSimulationResult,
        intent: CorporateIntent,
        frontier_health_score: float,
        consciousness_summary: Optional[ConsciousnessDashboardSummary] = None,
    ) -> StrategyEngineV2Report:
        """Generate an integrated strategy report for a scenario."""
        normalized_risk = self._scenario_risk_factor(simulation_result.scenario_type.value)
        alignment_score = self._compute_alignment_score(intent, frontier_health_score, normalized_risk)
        resilience_score = self._compute_resilience_score(simulation_result, intent, frontier_health_score)
        growth_score = self._compute_growth_commitment_score(intent, simulation_result)
        consciousness_alignment = self._compute_consciousness_alignment(intent, consciousness_summary)

        directives = self._build_directives(
            simulation_result,
            intent,
            frontier_health_score,
            alignment_score,
            resilience_score,
        )
        assets = self._build_strategic_assets(simulation_result, intent, frontier_health_score, consciousness_alignment)

        executive_summary = self._build_executive_summary(
            simulation_result,
            intent,
            frontier_health_score,
            alignment_score,
            resilience_score,
            growth_score,
        )
        recommendations = self._build_recommended_actions(directives, assets)

        reference_scores = {
            "scenario_score": float(getattr(simulation_result, "scenario_score", 0.0)),
            "scenario_risk_factor": normalized_risk,
            "intent_growth_weight": intent.growth_weight,
            "intent_profitability_weight": intent.profitability_weight,
            "frontier_health_score": frontier_health_score,
            "consciousness_alignment_score": consciousness_alignment,
        }

        return StrategyEngineV2Report(
            report_id=str(uuid4()),
            scenario_type=simulation_result.scenario_type,
            scenario_description=simulation_result.description,
            alignment_score=round(alignment_score, 3),
            risk_resilience_score=round(resilience_score, 3),
            growth_commitment_score=round(growth_score, 3),
            frontier_health_score=round(frontier_health_score, 3),
            consciousness_alignment_score=round(consciousness_alignment, 3),
            strategy_directives=directives,
            strategic_assets=assets,
            scenario_insights=self._build_scenario_insights(simulation_result, intent, frontier_health_score),
            executive_summary=executive_summary,
            recommended_actions=recommendations,
            reference_scores=reference_scores,
            context_notes=self._build_context_notes(simulation_result, consciousness_summary),
        )

    def _compute_alignment_score(self, intent: CorporateIntent, frontier_health_score: float, scenario_risk: float) -> float:
        intent_alignment = (
            intent.growth_weight * 0.28
            + intent.profitability_weight * 0.28
            + intent.innovation_weight * 0.22
            + intent.stability_weight * 0.22
        )
        score = (intent_alignment * 0.7) + (frontier_health_score * 0.2) + ((1.0 - scenario_risk) * 0.1)
        return min(max(score, 0.0), 1.0)

    def _compute_resilience_score(
        self,
        simulation_result: ScenarioSimulationResult,
        intent: CorporateIntent,
        frontier_health_score: float,
    ) -> float:
        scenario_risk = self._scenario_risk_factor(simulation_result.scenario_type.value)
        stability = intent.stability_weight
        score = (1.0 - scenario_risk) * 0.4 + stability * 0.3 + frontier_health_score * 0.3
        return min(max(score, 0.0), 1.0)

    def _compute_growth_commitment_score(
        self,
        intent: CorporateIntent,
        simulation_result: ScenarioSimulationResult,
    ) -> float:
        momentum = getattr(simulation_result, "scenario_score", 0.5)
        score = (intent.growth_weight * 0.55) + (intent.innovation_weight * 0.25) + ((momentum + 1.0) / 4.0)
        return min(max(score, 0.0), 1.0)

    def _compute_consciousness_alignment(
        self,
        intent: CorporateIntent,
        consciousness_summary: Optional[ConsciousnessDashboardSummary],
    ) -> float:
        if not consciousness_summary:
            return 0.5
        clarity = consciousness_summary.clarity_score
        alignment = consciousness_summary.alignment_score
        return min(max((clarity * 0.5) + (alignment * 0.5), 0.0), 1.0)

    def _scenario_risk_factor(self, scenario_type: str) -> float:
        mapping = {
            "recession": 0.9,
            "pessimistic": 0.8,
            "baseline": 0.5,
            "optimistic": 0.3,
            "tech_boom": 0.35,
        }
        return mapping.get(scenario_type, 0.6)

    def _build_directives(
        self,
        simulation_result: ScenarioSimulationResult,
        intent: CorporateIntent,
        frontier_health_score: float,
        alignment_score: float,
        resilience_score: float,
    ) -> List[StrategyDirective]:
        directives = []
        scenario_type = simulation_result.scenario_type.value
        risk_label = simulation_result.risk_assessment.lower()

        directives.append(StrategyDirective(
            directive_id="DIRECTIVE_01",
            name="Balance growth with resilience",
            description= (
                "Align growth ambitions with resilience by buffering cash and protecting core operations "
                "against scenario volatility."
            ),
            priority=min(1.0, max(0.6, intent.growth_weight + resilience_score * 0.3)),
            rationale=(
                f"This scenario requires a balanced agenda: {simulation_result.risk_assessment} risk and "
                f"{simulation_result.opportunity_assessment} opportunity imply both defense and selective expansion."
            ),
            directive_type="resilience",
        ))

        if intent.innovation_weight + intent.growth_weight > 0.5:
            directives.append(StrategyDirective(
                directive_id="DIRECTIVE_02",
                name="Embed innovation into execution",
                description=(
                    "Prioritize rapid experimentation, customer-facing pilots, and modular capabilities that can "
                    "scale if the scenario upside materializes."
                ),
                priority=min(1.0, intent.innovation_weight + intent.growth_weight * 0.4),
                rationale=(
                    "Innovation posture allows the enterprise to capture scenario upside while maintaining optionality."
                ),
                directive_type="growth",
            ))

        if frontier_health_score < 0.6:
            directives.append(StrategyDirective(
                directive_id="DIRECTIVE_03",
                name="Reinforce strategic frontier coverage",
                description=(
                    "Close gaps in the strategic frontier by adding differentiated options and preserving optionality."
                ),
                priority=0.9,
                rationale=(
                    "A weaker frontier raises the risk that the organization cannot pivot effectively under stress."
                ),
                directive_type="frontier",
            ))

        if risk_label in {"high", "severe", "critical"} or scenario_type in {"recession", "pessimistic"}:
            directives.append(StrategyDirective(
                directive_id="DIRECTIVE_04",
                name="Strengthen downside hedges",
                description=(
                    "Build contingency reserves, tighten cost governance, and protect customer retention in case "
                    "the negative scenario deepens."
                ),
                priority=min(1.0, resilience_score + 0.2),
                rationale=(
                    "Downside protection reduces exposure to scenario-driven shocks while preserving optionality."
                ),
                directive_type="risk_management",
            ))

        directives.append(StrategyDirective(
            directive_id="DIRECTIVE_05",
            name="Clarify narrative and execution intent",
            description=(
                "Translate the strategy into concrete decisions with clear ownership, metrics, and communication "
                "for the executive team."
            ),
            priority=0.85,
            rationale=(
                "Clear narrative alignment is needed to ensure strategy execution is not lost in complexity."
            ),
            directive_type="execution",
        ))

        return directives

    def _build_strategic_assets(
        self,
        simulation_result: ScenarioSimulationResult,
        intent: CorporateIntent,
        frontier_health_score: float,
        consciousness_alignment: float,
    ) -> List[StrategicAsset]:
        assets = []
        scenario_key = simulation_result.scenario_type.value
        asset_priority = max(0.45, min(1.0, frontier_health_score + intent.growth_weight * 0.2))

        assets.append(StrategicAsset(
            asset_id="ASSET_01",
            name="Adaptive Resource Allocation",
            asset_type="capability",
            description=(
                "Deploy a dynamic resource allocation process that adjusts investment levels by scenario, "
                "market signals, and operating performance."
            ),
            priority=asset_priority,
            expected_impact=min(1.0, 0.6 + consciousness_alignment * 0.3),
            dependencies=["financial_planning", "scenario_monitoring"],
        ))

        assets.append(StrategicAsset(
            asset_id="ASSET_02",
            name="Rapid Response Innovation Lab",
            asset_type="initiative",
            description=(
                "Establish a fast-cycle innovation lab to test new business models and customer propositions in "
                "the identified scenario context."
            ),
            priority=min(1.0, intent.innovation_weight + 0.3),
            expected_impact=min(1.0, 0.65 + (1.0 - frontier_health_score) * 0.15),
            dependencies=["cross-functional teams", "data_insights"],
        ))

        assets.append(StrategicAsset(
            asset_id="ASSET_03",
            name="Scenario-led Customer Retention Program",
            asset_type="execution",
            description=(
                "Build targeted retention initiatives and customer communications aligned to the scenario risk profile."
            ),
            priority=min(1.0, intent.stability_weight + 0.25),
            expected_impact=min(1.0, 0.65 + (1.0 - scenario_key.count("boom")) * 0.2),
            dependencies=["customer_insights", "marketing_execution"],
        ))

        if simulation_result.scenario_type.value in {"optimistic", "tech_boom"}:
            assets.append(StrategicAsset(
                asset_id="ASSET_04",
                name="Scale Expansion Backlog",
                asset_type="investment",
                description=(
                    "Prepare a prioritized set of scalable investments ready to accelerate when opportunity signals strengthen."
                ),
                priority=min(1.0, intent.growth_weight + intent.profitability_weight * 0.2),
                expected_impact=min(1.0, 0.7 + frontier_health_score * 0.2),
                dependencies=["investment_readiness", "capital_allocation"],
            ))

        return assets

    def _build_executive_summary(
        self,
        simulation_result: ScenarioSimulationResult,
        intent: CorporateIntent,
        frontier_health_score: float,
        alignment_score: float,
        resilience_score: float,
        growth_score: float,
    ) -> str:
        return (
            f"For the {simulation_result.scenario_type.value} scenario, the strategy should "
            f"protect core value while selectively investing in growth. The report blends intent-driven "
            f"priorities (growth={intent.growth_weight:.2f}, profitability={intent.profitability_weight:.2f}, "
            f"innovation={intent.innovation_weight:.2f}, stability={intent.stability_weight:.2f}) with "
            f"frontier health ({frontier_health_score:.2f}) and scenario resilience ({resilience_score:.2f}). "
            f"Recommended execution should emphasize clarity, optionality, and decisive risk management."
        )

    def _build_recommended_actions(
        self,
        directives: List[StrategyDirective],
        assets: List[StrategicAsset],
    ) -> List[str]:
        actions = []
        for directive in directives[:3]:
            actions.append(f"{directive.name}: {directive.rationale}")
        for asset in assets[:2]:
            actions.append(f"Build {asset.name} to improve impact and execution readiness.")
        return actions

    def _build_scenario_insights(
        self,
        simulation_result: ScenarioSimulationResult,
        intent: CorporateIntent,
        frontier_health_score: float,
    ) -> List[str]:
        return [
            f"Scenario prioritizes {simulation_result.risk_assessment.lower()} risk and {simulation_result.opportunity_assessment.lower()} opportunity.",
            f"Current frontier health is {frontier_health_score:.2f} which suggests a need for stronger optionality and coverage.",
            f"Intent signals strong commitment to {intent.cultural_identity or 'balanced'} posture with a growth/resilience mix."
        ]

    def _build_context_notes(
        self,
        simulation_result: ScenarioSimulationResult,
        consciousness_summary: Optional[ConsciousnessDashboardSummary],
    ) -> Optional[str]:
        if not consciousness_summary:
            return None
        return (
            f"Corporate consciousness is currently framed around {consciousness_summary.identity_statement}. "
            f"The next phase is {consciousness_summary.next_phase} and alignment score is {consciousness_summary.alignment_score:.2f}."
        )
