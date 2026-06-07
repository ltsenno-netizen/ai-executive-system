import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.models.executive_meeting_model import BoardDecision, ExecutiveMeetingState
from app.routes import executive_dashboard

client = TestClient(app)


def test_dashboard_includes_board_decision(monkeypatch):
    mock_state = ExecutiveMeetingState(
        month=8,
        agenda=[],
        decisions=[],
        next_month_projection={'revenue': 10.0, 'profit': 1.0, 'profit_margin': 0.1},
        executive_agents=[],
        debate_summary=None,
        decision_options=[],
        meeting_minutes=None,
        selected_option_id='B',
        ceo_comment='Check board summary',
        ceo_selected_option_id='B',
        ceo_selected_option_label='守り寄り成長案',
        ceo_decision_rationale='バランスを優先しました。',
        ceo_persona=None,
        board_decision=BoardDecision(
            status='conditional',
            final_option_id='B',
            final_option_label='バランス案',
            board_rationale='リスクは許容範囲だが、キャッシュ監視が必要。',
            conditions='キャッシュ残高が閾値を下回った場合は投資を一時停止。',
        ),
        decision_actor='AI CEO + Board',
    )

    monkeypatch.setattr(
        executive_dashboard.service.meeting_service,
        'load_latest_state_for_month',
        lambda month: mock_state,
    )
    executive_dashboard.service._dashboard_cache.clear()

    response = client.get('/api/executive/dashboard?month=8')
    assert response.status_code == 200

    data = response.json()
    meeting = data.get('meeting')
    assert meeting is not None
    assert meeting['board_status'] == 'conditional'
    assert 'キャッシュ' in meeting['board_rationale']
    assert '閾値' in meeting['board_conditions']
