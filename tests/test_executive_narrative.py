import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.services.executive_narrative_service import ExecutiveNarrativeService
from app.services.executive_narrative_engine import ExecutiveNarrativeEngine

client = TestClient(app)


def test_generate_monthly_narrative_structure():
    service = ExecutiveNarrativeService()
    narrative = service.generate_monthly_narrative(7)

    assert narrative.month == 7
    assert narrative.sentiment in {'Positive', 'Neutral', 'Negative'}
    assert isinstance(narrative.sections, list)
    assert len(narrative.key_drivers) > 0
    assert len(narrative.risks) > 0
    assert len(narrative.opportunities) > 0


def test_generate_annual_narrative_consistency():
    service = ExecutiveNarrativeService()
    annual = service.generate_annual_narrative(2026)

    assert annual.year == 2026
    assert isinstance(annual.major_events, list)
    assert len(annual.business_unit_stories) > 0
    assert 'outlook_next_year' in annual.__fields__
    assert isinstance(annual.strategic_shift, str)


def test_generate_monthly_narrative_includes_ai_ceo_final_decision():
    engine = ExecutiveNarrativeEngine()
    meeting_state = {
        'selected_option_id': 'B',
        'decision_options': [{'id': 'B', 'label': '守りの投資抑制', 'pros': [], 'cons': []}],
        'ceo_selected_option_label': '守りの投資抑制',
        'ceo_decision_rationale': 'キャッシュを守りつつ安定成長を目指すため。',
        'decision_actor': 'AI CEO',
    }
    narrative = engine.build_monthly_narrative(
        period='2026-07',
        financials={'cash_balance': 3.0, 'profit_margin': 0.2, 'profit': 1.0, 'revenue': {'A': 5.0}, 'short_term_debt': 1.0, 'long_term_debt': 0.5, 'available_credit_line': 2.0},
        market_state={'market_index_by_segment': {'AI': 1.0}, 'active_events': []},
        org_state={'units': [{'headcount': 50, 'workload_index': 0.9}]},
        meeting_state={
            **meeting_state,
            'ceo_persona': {
                'aggressiveness': 0.7,
                'risk_tolerance': 0.6,
                'brand_priority': 0.8,
                'short_term_focus': 0.6,
                'long_term_focus': 0.8,
            },
        },
    )

    assert narrative.decisions_section.final_decision_actor == 'AI CEO'
    assert narrative.decisions_section.final_decision_rationale == 'キャッシュを守りつつ安定成長を目指すため。'
    assert narrative.ceo_persona == {'aggressiveness': 0.7, 'risk_tolerance': 0.6, 'brand_priority': 0.8, 'short_term_focus': 0.6, 'long_term_focus': 0.8}
    assert '2026年のホリプロの興行・ライブ・IP強化戦略' in narrative.decision_commentary


def test_generate_multi_year_narrative_range():
    service = ExecutiveNarrativeService()
    narrative = service.generate_multi_year_narrative(2024, 2026)

    assert narrative.start_year == 2024
    assert narrative.end_year == 2026
    assert isinstance(narrative.transformation_story, str)
    assert len(narrative.growth_drivers) > 0
    assert len(narrative.structural_changes) > 0


def test_monthly_narrative_api():
    response = client.get('/api/narrative/monthly?month=7')
    assert response.status_code == 200
    body = response.json()
    assert body['month'] == 7
    assert 'sentiment' in body
    assert isinstance(body['sections'], list)


def test_annual_narrative_api():
    response = client.get('/api/narrative/annual?year=2026')
    assert response.status_code == 200
    body = response.json()
    assert body['year'] == 2026
    assert 'major_events' in body
    assert 'business_unit_stories' in body


def test_multi_year_narrative_api():
    response = client.get('/api/narrative/multiyear?start=2024&end=2026')
    assert response.status_code == 200
    body = response.json()
    assert body['start_year'] == 2024
    assert body['end_year'] == 2026
    assert 'transformation_story' in body
