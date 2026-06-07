from src.backend.app.models.corporate_consciousness_model import ConsciousnessDashboardSummary
from src.backend.app.models.corporate_intent_model import CorporateIntent
from src.backend.app.models.external_environment_model_v2 import ExternalEnvironmentState, PESTFactors, CompetitorAction
from src.backend.app.models.corporate_consciousness_evolution_model import ConsciousnessEvolutionState
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.scenario_model import ScenarioType
from src.backend.app.models.scenario_simulation_model import ScenarioSimulationResult
from src.backend.app.services.strategy_engine_v2 import StrategyEngineV2


def test_strategy_engine_v2_generates_report():
    engine = StrategyEngineV2()
    simulation_result = ScenarioSimulationResult(
        scenario_type=ScenarioType.BASELINE,
        description="Baseline execution path",
        duration_months=12,
        scenario_drivers={"market": "steady"},
        stress_factors={"economic": 0.1},
        narrative_focus="Stable demand with incremental growth",
        projected_environment=ExternalEnvironmentState(
            period="2026-01",
            pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.5),
            competitors=[CompetitorAction(competitor_name="Competitor A", aggressiveness=0.4, market_share_shift=0.02)],
            shocks=[],
            market_growth_modifier=0.02,
            risk_modifier=0.0,
        ),
        projected_culture=CultureProfile(
            period="2026-01",
            innovation_culture=0.6,
            people_culture=0.7,
            execution_culture=0.7,
            aggressiveness_culture=0.5,
            risk_aversion_culture=0.4,
            brand_culture=0.6,
            cost_culture=0.5,
            stability_culture=0.6,
        ),
        projected_consciousness_evolution=ConsciousnessEvolutionState(),
        financial_impact_summary={"revenue": 1000000.0, "profit": 150000.0},
        risk_assessment="Moderate",
        opportunity_assessment="Solid",
        scenario_score=0.6,
        confidence=0.75,
        contingency_recommendations=["Keep cash reserves stable"],
        strategic_implications=["Focus on margin improvement"],
    )

    intent = CorporateIntent(
        growth_weight=0.35,
        profitability_weight=0.25,
        innovation_weight=0.2,
        stability_weight=0.2,
        risk_preference=0.5,
        time_horizon=0.7,
        cultural_identity="balanced",
    )

    consciousness_summary = ConsciousnessDashboardSummary(
        consciousness_id="c-1",
        period="2026-01",
        identity_statement="Customer-centered innovator",
        purpose_statement="Deliver sustainable business value",
        strategic_direction="Balanced growth and resilience",
        current_phase="Intentional",
        next_phase="Emergent",
        overall_score=0.7,
        clarity_score=0.75,
        alignment_score=0.72,
        top_strengths=["clear purpose", "strong governance"],
        top_challenges=["cost management", "speed of execution"],
        strategic_implications=["Move faster on customer experimentation"],
        consciousness_statement_summary="A coherent purpose that balances growth and stability.",
        last_updated="2026-01-01T00:00:00",
    )

    report = engine.generate_strategy_report(
        simulation_result=simulation_result,
        intent=intent,
        frontier_health_score=0.55,
        consciousness_summary=consciousness_summary,
    )

    assert report.scenario_type == ScenarioType.BASELINE
    assert 0.0 <= report.alignment_score <= 1.0
    assert len(report.strategy_directives) >= 1
    assert len(report.strategic_assets) >= 1
    assert "strategy" in report.executive_summary.lower()
