import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.models.executive_narrative_model import DecisionRationale, ExecutiveNarrative
from app.models.executive_report_model import ExecutiveReport
from app.services.monthly_batch_service import MonthlyBatchService


def test_run_monthly_cycle_success(monkeypatch):
    service = MonthlyBatchService()

    monthly_state = {
        'financials': {
            'cash_balance': 5.0,
            'profit_margin': 0.25,
            'revenue': {'A': 10.0},
            'profit': 2.5,
        },
        'environment': {'market_index_by_segment': {}, 'active_events': []},
    }

    monkeypatch.setattr(
        service.integration_service,
        'simulate_month_full',
        lambda month, year=None, environment_state=None: monthly_state,
    )
    monkeypatch.setattr(
        service.integration_service.organization_service,
        'load_organization_state',
        lambda month: {'units': []},
    )
    monkeypatch.setattr(
        service.meeting_service,
        'build_meeting_agenda',
        lambda month: [],
    )
    monkeypatch.setattr(
        service.meeting_service,
        'generate_decision_options',
        lambda agenda: [{'id': 'A', 'label': 'Default', 'pros': ['pro'], 'cons': ['con']}],
    )

    class DummyDecision:
        def model_dump(self):
            return {
                'agenda_id': 'a',
                'decision': 'Approve',
                'comment': 'approved',
                'applied_effect': {},
            }

    monkeypatch.setattr(
        service.meeting_service,
        'apply_decision_option',
        lambda option_id, month, ceo_comment=None: [DummyDecision()],
    )
    monkeypatch.setattr(
        service.narrative_service,
        'generate_and_store_narrative',
        lambda period, financials, market_state, org_state, meeting_state: ExecutiveNarrative(
            period=period,
            summary='summary',
            financial_section='',
            market_section='',
            organization_section='',
            investment_section='',
            risk_section='',
            decisions_section=DecisionRationale(
                option_id='A',
                label='Default',
                pros=['pro'],
                cons=['con'],
                why_chosen='reason',
            ),
            next_month_focus=[],
        ),
    )
    monkeypatch.setattr(
        service.report_service,
        'generate_and_store_report',
        lambda period, narrative, financials, market_state, org_state: ExecutiveReport(
            period=period,
            title='title',
            management_summary='summary',
            sections=[],
        ),
    )
    monkeypatch.setattr(
        service.dashboard_service,
        'build_dashboard',
        lambda month: None,
    )

    result = service.run_monthly_cycle('2026-04')

    assert result.simulation_ok
    assert result.meeting_ok
    assert result.narrative_ok
    assert result.report_ok
    assert result.errors == []


def test_run_monthly_cycle_meeting_failure(monkeypatch):
    service = MonthlyBatchService()

    monthly_state = {
        'financials': {
            'cash_balance': 5.0,
            'profit_margin': 0.25,
            'revenue': {'A': 10.0},
            'profit': 2.5,
        },
        'environment': {'market_index_by_segment': {}, 'active_events': []},
    }

    monkeypatch.setattr(
        service.integration_service,
        'simulate_month_full',
        lambda month, year=None, environment_state=None: monthly_state,
    )

    def fail_meeting(month):
        raise RuntimeError('meeting failed')

    monkeypatch.setattr(
        service.meeting_service,
        'build_meeting_agenda',
        fail_meeting,
    )

    result = service.run_monthly_cycle('2026-04')

    assert result.simulation_ok
    assert not result.meeting_ok
    assert not result.narrative_ok
    assert not result.report_ok
    assert any('meeting failed' in error for error in result.errors)
