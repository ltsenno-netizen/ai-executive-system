import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.main import app

client = TestClient(app)


def test_get_latest_annual_report():
    """最新年次レポート取得APIのテスト"""
    response = client.get("/api/history/annual/latest")
    # データが存在しない場合は404
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert "year" in data
        assert "revenue_total" in data
        assert "profit_total" in data
        assert "evolution_trend" in data
        assert "major_events" in data


def test_get_annual_report():
    """指定年次レポート取得APIのテスト"""
    response = client.get("/api/history/annual/2024")
    # データが存在しない場合は404
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert data["year"] == 2024


def test_get_company_timeline():
    """企業タイムライン取得APIのテスト"""
    response = client.get("/api/history/timeline")
    assert response.status_code == 200
    data = response.json()
    assert "leadership_events" in data
    assert "annual_reports" in data
    assert isinstance(data["leadership_events"], list)
    assert isinstance(data["annual_reports"], list)