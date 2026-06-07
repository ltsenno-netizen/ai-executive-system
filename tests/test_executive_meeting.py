import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.services.executive_meeting_service import ExecutiveMeetingService

client = TestClient(app)


def test_build_meeting_agenda():
    service = ExecutiveMeetingService()
    agenda = service.build_meeting_agenda(7)

    assert len(agenda) >= 5
    assert any(item.category == 'PL' for item in agenda)
    assert any(item.category == 'Portfolio' for item in agenda)
    assert all(isinstance(item.ai_recommendation, str) for item in agenda)


def test_apply_decisions_and_next_month_projection():
    service = ExecutiveMeetingService()
    agenda = service.build_meeting_agenda(7)
    decision = {
        'agenda_id': agenda[0].id,
        'decision': 'Approve',
        'comment': 'Approve this recommendation',
    }
    state = service.simulate_executive_meeting(7, [decision])

    assert state.month == 7
    assert len(state.decisions) == 1
    assert state.next_month_projection['month'] == 8
    assert 'revenue' in state.next_month_projection
    assert 'profit' in state.next_month_projection


def test_get_meeting_agenda_api():
    response = client.get('/api/meeting/agenda?month=7')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(item['category'] == 'PL' for item in response.json())


def test_post_meeting_decisions_api():
    response = client.post(
        '/api/meeting/decide',
        json={
            'month': 7,
            'decisions': [
                {
                    'agenda_id': '7-pl',
                    'decision': 'Approve',
                    'comment': 'Approve PL recommendation',
                }
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['month'] == 7
    assert 'next_month_projection' in body
    assert body['decisions'][0]['decision'] == 'Approve'


def test_get_meeting_state_api():
    response = client.get('/api/meeting/state?month=7')
    assert response.status_code == 200
    body = response.json()
    assert body['month'] == 7
    assert 'next_month_projection' in body
    assert 'agenda' in body
