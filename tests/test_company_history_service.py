import os
import sys
import tempfile
import json

from src.backend.app.services.company_history_service import CompanyHistoryService
from src.backend.app.models.company_history_model import AnnualReport


def test_generate_annual_history():
    """年次歴史生成のテスト"""
    service = CompanyHistoryService()

    # 一時ディレクトリを使用
    with tempfile.TemporaryDirectory() as temp_dir:
        original_history_dir = service.history_dir
        service.history_dir = temp_dir

        try:
            year = 2024
            report = service.generate_annual_history(year)

            # レポートが生成されたか確認
            assert isinstance(report, AnnualReport)
            assert report.year == year

            # JSONファイルが保存されたか確認
            year_dir = os.path.join(temp_dir, str(year))
            report_path = os.path.join(year_dir, 'annual_report.json')
            assert os.path.exists(report_path)

            # JSONの内容を確認
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert data['year'] == year

        finally:
            service.history_dir = original_history_dir


def test_get_annual_report():
    """年次レポート取得のテスト"""
    service = CompanyHistoryService()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_history_dir = service.history_dir
        service.history_dir = temp_dir

        try:
            # レポートを作成
            year = 2024
            report = service.generate_annual_history(year)

            # 取得テスト
            retrieved = service.get_annual_history(year)
            assert retrieved is not None
            assert retrieved.year == year
            assert retrieved.revenue_total == report.revenue_total

            # 存在しない年のテスト
            not_found = service.get_annual_history(2020)
            assert not_found is None

        finally:
            service.history_dir = original_history_dir


def test_get_latest_annual_report():
    """最新年次レポート取得のテスト"""
    service = CompanyHistoryService()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_history_dir = service.history_dir
        service.history_dir = temp_dir

        try:
            # 複数のレポートを作成
            service.generate_annual_history(2023)
            service.generate_annual_history(2024)
            service.generate_annual_history(2022)

            latest = service.get_latest_annual_history()
            assert latest is not None
            assert latest.year == 2024  # 最新の年

        finally:
            service.history_dir = original_history_dir


def test_generate_timeline():
    """タイムライン生成のテスト"""
    service = CompanyHistoryService()

    timeline = service.generate_timeline()

    # 基本構造の確認
    assert hasattr(timeline, 'leadership_events')
    assert hasattr(timeline, 'annual_reports')
    assert isinstance(timeline.leadership_events, list)
    assert isinstance(timeline.annual_reports, list)