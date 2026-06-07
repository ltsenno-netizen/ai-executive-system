import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.models.executive_report_model import ExecutiveReport
from app.routes import executive_dashboard

client = TestClient(app)


def test_dashboard_includes_latest_report(monkeypatch):
    executive_dashboard.service._dashboard_cache.clear()
    latest_report = ExecutiveReport(
        period='2026-04',
        title='月次経営レポート — 2026年4月',
        management_summary='4月は市場ショックと投資判断が重なり、守りと攻めのバランスが問われた月でした。',
        sections=[],
    )

    monkeypatch.setattr(
        executive_dashboard.service.report_service,
        'get_latest_report',
        lambda: latest_report,
    )
    monkeypatch.setattr(
        executive_dashboard.service.report_service,
        'list_reports',
        lambda limit=6: [
            {
                'period': '2026-04',
                'title': '月次経営レポート — 2026年4月',
                'summary': '4月は市場ショックと投資判断が重なり、守りと攻めのバランスが問われた月でした。',
            },
        ],
    )

    response = client.get('/api/executive/dashboard?month=4')
    assert response.status_code == 200
    data = response.json()

    assert data['latest_report_period'] == '2026-04'
    assert data['latest_report_title'] == '月次経営レポート — 2026年4月'
    assert '市場ショック' in data['latest_report_summary']


def test_dashboard_report_history(monkeypatch):
    executive_dashboard.service._dashboard_cache.clear()
    history = [
        {
            'period': '2026-04',
            'title': 'R1',
            'summary': 'AAA',
        },
        {
            'period': '2026-03',
            'title': 'R2',
            'summary': 'BBB',
        },
    ]

    monkeypatch.setattr(
        executive_dashboard.service.report_service,
        'get_latest_report',
        lambda: ExecutiveReport(period='2026-04', title='R1', management_summary='AAA', sections=[]),
    )
    monkeypatch.setattr(
        executive_dashboard.service.report_service,
        'list_reports',
        lambda limit=6: history,
    )

    response = client.get('/api/executive/dashboard?month=4')
    assert response.status_code == 200
    data = response.json()

    assert len(data['reports']) == 2
    assert data['reports'][0]['period'] == '2026-04'
    assert data['reports'][1]['period'] == '2026-03'


def test_dashboard_no_reports(monkeypatch):
    executive_dashboard.service._dashboard_cache.clear()
    monkeypatch.setattr(
        executive_dashboard.service.report_service,
        'get_latest_report',
        lambda: None,
    )
    monkeypatch.setattr(
        executive_dashboard.service.report_service,
        'list_reports',
        lambda limit=6: [],
    )

    response = client.get('/api/executive/dashboard?month=4')
    assert response.status_code == 200
    data = response.json()

    assert data['latest_report_period'] is None
    assert data['latest_report_title'] is None
    assert data['latest_report_summary'] is None
    assert data['reports'] == []
