import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app

client = TestClient(app)


class TestExecutiveAgentsAPI:
    """Executive Agents API のテスト"""
    
    def test_get_agents(self):
        """エージェント一覧取得"""
        response = client.get("/api/executives/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert data["count"] == 6
    
    def test_get_agents_structure(self):
        """エージェント構造"""
        response = client.get("/api/executives/agents")
        
        assert response.status_code == 200
        data = response.json()
        
        agent = data["agents"][0]
        assert "role" in agent
        assert "name" in agent
        assert "focus_area" in agent
        assert "vote_weight" in agent
        assert "weights" in agent
        assert "characteristics" in agent
    
    def test_run_decision(self):
        """経営会議実行"""
        response = client.post("/api/executives/decide")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "decision" in data
        assert "summary" in data
        assert "votes" in data
        assert "perspectives" in data
        
        decision = data["decision"]
        assert "selected_candidate_id" in decision
        assert "aggregated_score" in decision
        assert "method" in decision
    
    def test_council_summary(self):
        """経営会議概要"""
        response = client.get("/api/executives/council-summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "agent_count" in data
        assert "candidate_count" in data
        assert "selected_strategy" in data
        assert "consensus_level" in data
    
    def test_perspectives(self):
        """各エージェントの視点"""
        response = client.get("/api/executives/perspectives")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "perspectives" in data
        perspectives = data["perspectives"]
        
        for p in perspectives:
            assert "role" in p
            assert "focus" in p
            assert "top_choice" in p
            assert "score" in p
    
    def test_markdown(self):
        """Markdown 出力"""
        response = client.get("/api/executives/markdown")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "markdown" in data
        assert "経営チームエージェント" in data["markdown"]
    
    def test_reset_agents(self):
        """エージェントリセット"""
        response = client.post("/api/executives/agents/reset")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "count" in data
        assert data["count"] == 6


class TestExecutiveAgentsAPIValidation:
    """API バリデーションテスト"""
    
    def test_update_agent_validation(self):
        """エージェント更新のバリデーション"""
        # 無効なロールで更新
        response = client.post(
            "/api/executives/agents",
            json={
                "role": "INVALID",
                "updates": {"growth_weight": 0.4}
            }
        )
        
        # エラーになることを確認
        assert response.status_code in [400, 422]
    
    def test_decision_with_invalid_data(self):
        """無効データでの決定"""
        # 無効な frontier_id
        response = client.post(
            "/api/executives/decide",
            json={"frontier_id": "invalid_id"}
        )
        
        # 200 または エラー
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])