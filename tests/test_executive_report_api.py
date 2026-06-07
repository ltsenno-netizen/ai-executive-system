import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.routes import executive_report

client = TestClient(app)


def test_get_latest_report_api(monkeypatch):
    monkeypatch.setattr(
        executive_report.service,
        'list_reports',
        lambda limit=1: [{'period': '2026-04', 'title': '月次経営レポート 2026年4月'}],
    )
    monkeypatch.setattr(
        executive_report.service,
        'get_report',
        lambda period: '# 月次経営レポート — 2026年4月\n...\n',
    )

    response = client.get('/api/reports/latest')
    assert response.status_code == 200
    data = response.json()
    assert data['period'] == '2026-04'
    assert data['title'] == '月次経営レポート 2026年4月'
    assert '# 月次経営レポート — 2026年4月' in data['content']


def test_get_report_by_period_api(monkeypatch):
    monkeypatch.setattr(
        executive_report.service,
        'get_report',
        lambda period: '# 月次経営レポート — 2026年4月\n...\n',
    )
    monkeypatch.setattr(
        executive_report.service,
        'list_reports',
        lambda limit=1: [{'period': '2026-04', 'title': '月次経営レポート 2026年4月'}],
    )

    response = client.get('/api/reports/2026/4')
    assert response.status_code == 200
    data = response.json()
    assert data['period'] == '2026-04'
    assert 'content' in data


def test_get_report_history_api(monkeypatch):
    monkeypatch.setattr(
        executive_report.service,
        'list_reports',
        lambda limit=6: [
            {'period': '2026-04', 'title': '月次経営レポート 2026年4月'},
            {'period': '2026-03', 'title': '月次経営レポート 2026年3月'},
        ],
    )

    response = client.get('/api/reports/history?limit=2')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['period'] == '2026-04'
