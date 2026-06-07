import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.services.executive_meeting_service import ExecutiveMeetingService

client = TestClient(app)


def test_generate_decision_options():
    service = ExecutiveMeetingService()
    agenda = service.build_meeting_agenda(5)
    options = service.generate_decision_options(agenda)

    assert len(options) == 3
    assert {option.id for option in options} == {'A', 'B', 'C'}
    assert all(isinstance(option.actions, list) for option in options)


def test_run_executive_debate():
    service = ExecutiveMeetingService()
    agenda = service.build_meeting_agenda(5)
    agents = service.build_executive_agents(agenda)
    debate = service.run_executive_debate(agenda, agents)

    assert len(agents) == 4
    assert debate.consensus
    assert isinstance(debate.cross_discussion, list)
    assert len(debate.opening_statements) == 4


def test_simulate_executive_meeting_with_ai_ceo(monkeypatch):
    service = ExecutiveMeetingService()

    monthly_state = {
        'financials': {'cash_balance': 1.5, 'profit_margin': 0.2, 'revenue': {'A': 10.0}, 'profit': 2.0},
        'environment': {'market_index_by_segment': {'A': 0.8}, 'active_events': []},
    }

    monkeypatch.setattr(
        service.integration_service,
        'simulate_month_full',
        lambda month, year=None, environment_state=None: monthly_state,
    )
    from app.services.executive_narrative_service import ExecutiveNarrativeService
    from app.models.executive_narrative_model import ExecutiveNarrative, DecisionRationale

    monkeypatch.setattr(
        service.integration_service.organization_service,
        'load_organization_state',
        lambda month: {'units': [{'workload_index': 1.2, 'headcount': 50}]},
    )
    monkeypatch.setattr(
        service.integration_service,
        'store_executive_report',
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        service,
        'save_meeting_state',
        lambda state: None,
    )
    monkeypatch.setattr(
        ExecutiveNarrativeService,
        'generate_and_store_narrative',
        lambda *args, **kwargs: ExecutiveNarrative(
            period='2026-05',
            summary='summary',
            financial_section='',
            market_section='',
            organization_section='',
            investment_section='',
            risk_section='',
            decisions_section=DecisionRationale(
                option_id='B',
                label='守り',
                pros=[],
                cons=[],
                why_chosen='AI CEO decision.',
            ),
            next_month_focus=[],
        ),
    )

    state = service.simulate_executive_meeting_with_ai_ceo(5)

    assert state.ceo_selected_option_label is not None
    assert state.ceo_decision_rationale is not None
    assert state.decision_actor == 'AI CEO + Board'
    assert state.board_decision is not None
    assert state.board_decision.status in {'approved', 'conditional', 'rejected'}


def test_get_meeting_options_api():
    response = client.get('/api/meeting/options?month=5')
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert body[0]['id'] in {'A', 'B', 'C'}


def test_get_meeting_debate_api():
    response = client.get('/api/meeting/debate?month=5')
    assert response.status_code == 200
    body = response.json()
    assert 'opening_statements' in body
    assert 'cross_discussion' in body
    assert body['consensus']


def test_post_meeting_decision_api():
    response = client.post(
        '/api/meeting/decision',
        json={
            'month': 5,
            'option_id': 'C',
            'ceo_comment': 'Choose balanced growth with risk controls.',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['month'] == 5
    assert body['selected_option_id'] == 'C'
    assert body['meeting_minutes']['summary']
    assert body['meeting_minutes']['ceo_comment'] == 'Choose balanced growth with risk controls.'
