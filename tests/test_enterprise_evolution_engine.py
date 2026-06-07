import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from enterprise_evolution_engine import EnterpriseEvolutionEngine
from app.models.culture_model import CultureProfile
from app.models.external_environment_model_v2 import ExternalEnvironmentState, PESTFactors, CompetitorAction, MarketShock
from executive_team_succession_model import ExecutivePersona, ExecutiveRole
from app.models.executive_meeting_model import BoardDecision


def test_environment_to_culture_shift():
    engine = EnterpriseEvolutionEngine()
    environment = ExternalEnvironmentState(
        period="2026-01",
        pest=PESTFactors(economic=0.2, political=0.5, social=0.5, technological=0.5),
        competitors=[CompetitorAction(competitor_name="Comp1", aggressiveness=0.8, market_share_shift=0.0)],
        shocks=[],
        market_growth_modifier=0.2,
        risk_modifier=0.5
    )
    culture = CultureProfile(
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
        stability_culture=0.5
    )
    executive_team = {}
    board_decisions = []

    result = engine.compute_enterprise_evolution(culture, environment, executive_team, board_decisions)

    assert result.environment_pressure > 0
    assert result.evolution_score > 0
    assert 'stability_culture' in result.culture_shift  # Due to low economic


def test_culture_to_leadership_shift():
    engine = EnterpriseEvolutionEngine()
    culture = CultureProfile(
        period="2026-01",
        innovation_culture=0.5,
        people_culture=0.8,
        process_culture=0.5,
        market_culture=0.5,
        aggressiveness_culture=0.5,
        risk_aversion_culture=0.5,
        brand_culture=0.5,
        cost_culture=0.5,
        execution_culture=0.5,
        stability_culture=0.5
    )
    environment = ExternalEnvironmentState(
        period="2026-01",
        pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.5),
        competitors=[],
        shocks=[],
        market_growth_modifier=0.0,
        risk_modifier=0.5
    )
    executive_team = {
        ExecutiveRole.CHRO: ExecutivePersona(
            role=ExecutiveRole.CHRO,
            financial_focus=0.5,
            operational_focus=0.5,
            brand_focus=0.5,
            people_focus=0.5,
            risk_tolerance=0.5,
            innovation_bias=0.5,
        )
    }
    board_decisions = []

    result = engine.compute_enterprise_evolution(culture, environment, executive_team, board_decisions)

    assert 'chro_people_focus' in result.leadership_shift


def test_leadership_to_culture_shift():
    engine = EnterpriseEvolutionEngine()
    culture = CultureProfile(
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
        stability_culture=0.5
    )
    environment = ExternalEnvironmentState(
        period="2026-01",
        pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.5),
        competitors=[],
        shocks=[],
        market_growth_modifier=0.0,
        risk_modifier=0.5
    )
    executive_team = {
        ExecutiveRole.CFO: ExecutivePersona(
            role=ExecutiveRole.CFO,
            financial_focus=0.5,
            operational_focus=0.5,
            brand_focus=0.5,
            people_focus=0.5,
            risk_tolerance=0.2,  # Conservative
            innovation_bias=0.5,
        )
    }
    board_decisions = []

    result = engine.compute_enterprise_evolution(culture, environment, executive_team, board_decisions)

    assert 'risk_aversion_culture' in result.culture_shift


def test_evolution_score_calculation():
    engine = EnterpriseEvolutionEngine()
    culture = CultureProfile(
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
        stability_culture=0.5
    )
    environment = ExternalEnvironmentState(
        period="2026-01",
        pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.5),
        competitors=[],
        shocks=[],
        market_growth_modifier=0.0,
        risk_modifier=0.5
    )
    executive_team = {}
    board_decisions = []

    result = engine.compute_enterprise_evolution(culture, environment, executive_team, board_decisions)

    assert isinstance(result.evolution_score, float)
    assert result.evolution_score >= 0