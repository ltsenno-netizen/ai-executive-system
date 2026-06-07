import os
import sys
import tempfile
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.models.improvement_cycle_model import ImprovementHistory
from app.services.improvement_cycle_service import ImprovementCycleService


def test_load_cycle_state():
    service = ImprovementCycleService()
    state = service.load_cycle_state()

    assert state.month == 0
    assert state.updated_priorities['performance_review_meeting'] == 1.0
    assert len(state.action_effectiveness) == 3


def test_update_action_priority_clips_values():
    service = ImprovementCycleService()
    history = ImprovementHistory(
        id='h1',
        month=1,
        issue_id='weak_performance_profit_margin',
        action_id='performance_review_meeting',
        expected_effect={'performance_profit_margin': 0.03},
        actual_effect={'performance_profit_margin': 0.08},
        effect_error={'performance_profit_margin': -0.05},
        priority_score=1.0,
    )

    updated = service.update_action_priority([history], {'performance_review_meeting': 1.0})

    assert updated['performance_review_meeting'] >= 0.1
    assert updated['performance_review_meeting'] <= 5.0


def test_simulate_month_cycle_e2e():
    with tempfile.TemporaryDirectory() as temp_dir:
        sample_state_file = os.path.join(temp_dir, 'improvement_cycle_state.json')
        original_state_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'samples', 'improvement_cycle_state.json'))
        shutil.copyfile(original_state_file, sample_state_file)

        service = ImprovementCycleService(data_path=temp_dir)
        result = service.simulate_month_cycle(1)

        assert result['month'] == 1
        assert 'pl' in result
        assert 'operations' in result
        assert 'issues' in result
        assert 'actions_executed' in result
        assert 'effectiveness' in result
        assert 'updated_priorities' in result
        assert isinstance(result['updated_priorities'], dict)

        state = service.load_cycle_state()
        assert state.month == 2
        assert len(state.executed_actions) == len(result['actions_executed'])
