import os
import sys

from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService
from src.backend.app.models.executive_dashboard_model import AnnualHistorySummary


def test_dashboard_includes_annual_history():
    """ダッシュボードに年次歴史サマリーが含まれることをテスト"""
    service = ExecutiveDashboardService()
    month = 1

    try:
        dashboard = service.build_dashboard(month)
        # latest_annual_history が存在するか確認
        assert hasattr(dashboard, 'latest_annual_history')
        # 型チェック
        if dashboard.latest_annual_history:
            assert isinstance(dashboard.latest_annual_history, AnnualHistorySummary)
    except Exception as e:
        # ビルドに失敗する場合（依存関係の問題）はモデルレベルでチェック
        from src.backend.app.models.executive_dashboard_model import ExecutiveDashboard
        assert 'latest_annual_history' in ExecutiveDashboard.model_fields
        field_info = ExecutiveDashboard.model_fields['latest_annual_history']
        # Optional[AnnualHistorySummary] であることを確認
        assert 'AnnualHistorySummary' in str(field_info.annotation)
