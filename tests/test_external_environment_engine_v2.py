import os
import sys
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.external_environment_engine_v2 import build_external_environment_state
from app.models.external_environment_model_v2 import (
    ExternalEnvironmentState,
    PESTFactors,
    CompetitorAction,
)


def test_build_external_environment_state_changes_pest_and_includes_competitors():
    previous_state = ExternalEnvironmentState(
        period='2026-01',
        pest=PESTFactors(political=0.5, economic=0.5, social=0.5, technological=0.5),
        competitors=[CompetitorAction(competitor_name='Existing', aggressiveness=0.2, market_share_shift=0.0)],
        shocks=[],
        market_growth_modifier=0.0,
        risk_modifier=0.0,
    )

    with patch('app.services.external_environment_engine_v2.random.uniform', side_effect=[0.02, -0.01, 0.7, 0.0, 0.7, 0.0]), \
         patch('app.services.external_environment_engine_v2.random.random', return_value=0.2):
        env = build_external_environment_state('2026-02', previous_state)

    assert env.period == '2026-02'
    assert 0.0 <= env.pest.economic <= 1.0
    assert 0.0 <= env.pest.social <= 1.0
    assert 0.0 <= env.pest.technological <= 1.0
    assert len(env.competitors) == 2
    assert all(0.0 <= comp.aggressiveness <= 1.0 for comp in env.competitors)
    assert env.market_growth_modifier != 0.0


def test_build_external_environment_state_applies_recession_shock():
    previous_state = ExternalEnvironmentState(
        period='2026-01',
        pest=PESTFactors(political=0.5, economic=0.5, social=0.5, technological=0.5),
        competitors=[CompetitorAction(competitor_name='Existing', aggressiveness=0.1, market_share_shift=0.0)],
        shocks=[],
        market_growth_modifier=0.0,
        risk_modifier=0.0,
    )

    with patch('app.services.external_environment_engine_v2.random.uniform', side_effect=[0.0, 0.0, 0.2, 0.0, 0.2, 0.0, 0.4]), \
         patch('app.services.external_environment_engine_v2.random.random', return_value=0.05), \
         patch('app.services.external_environment_engine_v2.random.choice', return_value='recession'), \
         patch('app.services.external_environment_engine_v2.random.randint', return_value=3):
        env = build_external_environment_state('2026-02', previous_state)

    assert any(shock.shock_type == 'recession' for shock in env.shocks)
    assert env.market_growth_modifier < 0.0
    assert env.risk_modifier > 0.0
