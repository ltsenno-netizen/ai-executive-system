import pytest
from src.backend.app.services.scenario_simulation_engine import ScenarioSimulationEngine
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.external_environment_model_v2 import ExternalEnvironmentState, PESTFactors, CompetitorAction
from src.backend.app.models.corporate_consciousness_evolution_model import ConsciousnessEvolutionState
from src.backend.app.models.scenario_model import ScenarioType


def test_generate_simulation_definitions():
    engine = ScenarioSimulationEngine()
    definitions = engine.generate_simulation_definitions()

    assert len(definitions) == 5
    assert any(d.scenario_type == ScenarioType.BASELINE for d in definitions)
    assert any(d.scenario_type == ScenarioType.OPTIMISTIC for d in definitions)
    assert any(d.scenario_type == ScenarioType.PESSIMISTIC for d in definitions)
    assert any(d.scenario_type == ScenarioType.TECH_BOOM for d in definitions)
    assert any(d.scenario_type == ScenarioType.RECESSION for d in definitions)


def test_run_scenario_simulation():
    engine = ScenarioSimulationEngine()
    definition = engine.generate_simulation_definitions()[1]

    current_culture = CultureProfile(
        period="2026-01",
        innovation_culture=0.5,
        people_culture=0.5,
        process_culture=0.5,
        market_culture=0.5,
        aggressiveness_culture=0.5,
        risk_aversion_culture=0.5,
        brand_culture=0.5,
        cost_culture=0.5,
        execution_culture=0.5,
        stability_culture=0.5,
    )

    current_environment = ExternalEnvironmentState(
        period="2026-01",
        pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.5),
        competitors=[CompetitorAction(competitor_name="Competitor A", aggressiveness=0.5, market_share_shift=0.3)],
        shocks=[],
        market_growth_modifier=0.02,
        risk_modifier=0.0,
    )

    current_evolution_state = ConsciousnessEvolutionState()
    current_financials = {"revenue": 1_000_000, "profit": 100_000, "cash": 5_000_000}

    result = engine.run_simulation(
        definition,
        current_culture,
        current_environment,
        current_evolution_state,
        current_financials,
    )

    assert result.scenario_type == definition.scenario_type
    assert result.description == definition.description
    assert isinstance(result.projected_environment, ExternalEnvironmentState)
    assert isinstance(result.projected_culture, CultureProfile)
    financial_summary = result.financial_impact_summary
    assert financial_summary is not None
    assert result.risk_assessment in ["Low", "Medium", "High"]
    assert result.opportunity_assessment in ["Low", "Medium", "High"]
    assert 0.0 <= result.scenario_score <= 1.0
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.contingency_recommendations, list)
    assert isinstance(result.strategic_implications, list)


def test_simulation_environment_projection_reflects_modifiers():
    engine = ScenarioSimulationEngine()
    baseline = engine.generate_simulation_definitions()[0]
    current_env = ExternalEnvironmentState(
        period="2026-01",
        pest=PESTFactors(economic=0.4, political=0.4, social=0.4, technological=0.4),
        competitors=[CompetitorAction(competitor_name="Competitor A", aggressiveness=0.4, market_share_shift=0.3)],
        shocks=[],
        market_growth_modifier=0.02,
        risk_modifier=0.0,
    )

    projected_env = engine._project_environment(current_env, baseline.environment_modifiers, baseline.stress_factors)
    assert projected_env.market_growth_modifier >= current_env.market_growth_modifier - 0.1
    assert 0.0 <= projected_env.pest.economic <= 1.0


def test_simulation_consciousness_evolution_creates_event():
    engine = ScenarioSimulationEngine()
    projected_env = ExternalEnvironmentState(
        period="2026-01",
        pest=PESTFactors(economic=0.2, political=0.3, social=0.4, technological=0.8),
        competitors=[CompetitorAction(competitor_name="Competitor A", aggressiveness=0.7, market_share_shift=0.2)],
        shocks=[],
        market_growth_modifier=-0.05,
        risk_modifier=0.2,
    )
    current_state = ConsciousnessEvolutionState()
    definition = engine.generate_simulation_definitions()[2]

    next_state = engine._project_consciousness_evolution(current_state, projected_env, CultureProfile(
        period="2026-01",
        innovation_culture=0.4,
        people_culture=0.4,
        process_culture=0.4,
        market_culture=0.4,
        aggressiveness_culture=0.4,
        risk_aversion_culture=0.4,
        brand_culture=0.4,
        cost_culture=0.4,
        execution_culture=0.4,
        stability_culture=0.4,
    ), definition)

    assert next_state.history
    assert next_state.history[-1].event_id.startswith("scenario-")
    assert 0.0 <= next_state.momentum <= 1.0
    assert 0.0 <= next_state.stability <= 1.0
