import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.models.executive_narrative_model import DecisionRationale, ExecutiveNarrative
from app.routes import executive_dashboard

client = TestClient(app)


def test_dashboard_includes_latest_narrative(monkeypatch):
    narrative = ExecutiveNarrative(
        period='2026-04',
        summary='4月は市場ショックと投資判断が重なり、資本配分の軸足が変化しました。',
        financial_section='資本状況は依然として安定しています。',
        market_section='市場はボラティリティが高まりつつあります。',
        organization_section='組織改革が着実に進行しています。',
        investment_section='投資は成長領域に重点が置かれました。',
        risk_section='リスク管理はより一層厳格化されました。',
        decisions_section=DecisionRationale(
            option_id='A',
            label='積極投資',
            pros=['成長機会の獲得', '市場シェア拡大'],
            cons=['短期キャッシュフローへの圧迫', '実行リスク'],
            why_chosen='成長軸を優先し、長期的価値向上を目指したため。',
        ),
        next_month_focus=['収益性の高い顧客セグメントに集中する', 'リスク管理を強化する'],
    )

    executive_dashboard.service._dashboard_cache.clear()
    monkeypatch.setattr(
        executive_dashboard.service.narrative_service,
        'get_latest_narrative',
        lambda: narrative,
    )

    response = client.get('/api/executive/dashboard?month=4')
    assert response.status_code == 200

    data = response.json()
    assert data['latest_narrative_period'] == '2026-04'
    assert '市場ショック' in data['latest_narrative_summary']
    assert data['latest_narrative_period'] is not None
    assert data['latest_narrative_summary'] is not None


def test_dashboard_meeting_timeline_contains_narrative_keys():
    executive_dashboard.service._dashboard_cache.clear()
    response = client.get('/api/executive/dashboard?month=7')
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data.get('meeting_timeline'), list)
    assert len(data['meeting_timeline']) > 0

    first_timeline = data['meeting_timeline'][0]
    assert 'selected_option_id' in first_timeline
    assert 'selected_option_label' in first_timeline
    assert 'meeting_risk_level' in first_timeline


def test_dashboard_latest_narrative_fallback_when_missing(monkeypatch):
    def raise_not_found():
        raise FileNotFoundError('No narratives available')

    executive_dashboard.service._dashboard_cache.clear()
    monkeypatch.setattr(
        executive_dashboard.service.narrative_service,
        'get_latest_narrative',
        raise_not_found,
    )

    response = client.get('/api/executive/dashboard?month=4')
    assert response.status_code == 200

    data = response.json()
    assert data['latest_narrative_period'] is None
    assert data['latest_narrative_summary'] is None
