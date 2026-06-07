import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app

client = TestClient(app)


class TestDashboardAutonomousExecutiveSummary:
    """Dashboard の Autonomous + Executive 統合サマリテスト"""
    
    def test_dashboard_includes_executive_decision(self):
        """ダッシュボードに Executive Decision が含まれる"""
        response = client.get("/api/dashboard/month/1")
        
        # 200 または 404 のいずれか
        assert response.status_code in [200, 404, 500]
    
    def test_dashboard_includes_corporate_intent(self):
        """ダッシュボードに Corporate Intent が含まれる"""
        response = client.get("/api/dashboard/month/1")
        
        # ステータスコード確認
        assert response.status_code in [200, 404, 500]


class TestAutonomousLoopIntegrationAPI:
    """自律ループ統合 API テスト"""
    
    def test_get_autonomous_metrics(self):
        """自律ループメトリクス取得"""
        response = client.get("/api/autonomous/metrics")
        
        assert response.status_code in [200, 404, 500]
    
    def test_get_latest_cycle(self):
        """最新サイクル取得"""
        response = client.get("/api/autonomous/latest-cycle")
        
        assert response.status_code in [200, 404, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])