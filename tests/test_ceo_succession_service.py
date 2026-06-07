import os
import sys
import tempfile
from unittest.mock import Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.ceo_succession_service import CeoSuccessionService
from app.models.ai_ceo_model import AICeoPersona


def test_run_ceo_succession_creates_decision_and_saves_persona():
    with tempfile.TemporaryDirectory() as root_dir:
        service = CeoSuccessionService(succession_root=root_dir, persona_root=root_dir)
        current_persona = AICeoPersona(
            aggressiveness=0.5,
            risk_tolerance=0.6,
            brand_priority=0.6,
            short_term_focus=0.4,
            long_term_focus=0.7,
        )
        service.ceo_learning_service.get_latest_persona = Mock(return_value=current_persona)
        service.ceo_learning_service.build_learning_history = Mock(return_value=[])

        decision = service.run_ceo_succession(
            '2026-01',
            current_financials={'cash_balance': 5.0, 'operating_profit': 1.0},
            market_state={'volatility': 0.1},
            org_state={'units': [{'workload_index': 0.5}]},
        )

        assert decision.period == '2026-01'
        assert decision.selected_candidate_id in {'A', 'B', 'C'}
        assert os.path.exists(os.path.join(root_dir, '2026-01.json'))
        latest = service.get_latest_succession_decision()
        assert latest is not None
        assert latest.period == '2026-01'
