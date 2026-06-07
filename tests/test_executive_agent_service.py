import pytest
from src.backend.app.services.executive_agent_service import ExecutiveAgentService
from src.backend.app.models.executive_agent_model import ExecutiveRole


class TestExecutiveAgentService:
    """Executive Agent Service のテスト"""
    
    def setup_method(self):
        """テスト前のセットアップ"""
        self.service = ExecutiveAgentService()
    
    def test_get_default_agents(self):
        """デフォルトエージェントの取得"""
        agents = self.service.get_default_agents()
        
        assert len(agents) == 6  # CEO, CFO, CMO, CTO, CHRO, COO
        
        roles = [a.role for a in agents]
        assert ExecutiveRole.CEO in roles
        assert ExecutiveRole.CFO in roles
        assert ExecutiveRole.CMO in roles
        assert ExecutiveRole.CTO in roles
        assert ExecutiveRole.CHRO in roles
        assert ExecutiveRole.COO in roles
    
    def test_default_agent_weights(self):
        """デフォルトエージェントの重み"""
        agents = self.service.get_default_agents()
        
        ceo = next(a for a in agents if a.role == ExecutiveRole.CEO)
        assert ceo.vote_weight == 1.5
        assert ceo.growth_weight > ceo.stability_weight  # CEO は成長志向
        
        cfo = next(a for a in agents if a.role == ExecutiveRole.CFO)
        assert cfo.profitability_weight > cfo.growth_weight  # CFO は収益性志向
        assert cfo.cost_sensitivity > 0.7  # コスト敏感
        
        chro = next(a for a in agents if a.role == ExecutiveRole.CHRO)
        assert chro.people_focus > 0.7  # 人材重視
    
    def test_get_agents(self):
        """エージェント取得（設定から）"""
        agents = self.service.get_agents()
        
        assert len(agents) > 0
        assert all(a.role is not None for a in agents)
    
    def test_save_agents(self):
        """エージェント設定の保存"""
        agents = self.service.get_default_agents()
        
        result = self.service.save_agents(agents, reason="Test save")
        
        assert result is True
    
    def test_update_agent(self):
        """エージェント更新"""
        updates = {
            "growth_weight": 0.4,
            "risk_aversion": 0.6,
        }
        
        updated = self.service.update_agent(ExecutiveRole.CEO, updates)
        
        assert updated.role == ExecutiveRole.CEO
        assert updated.growth_weight == 0.4
    
    def test_run_executive_decision(self):
        """経営会議の実行"""
        result = self.service.run_executive_decision()
        
        assert result.selected_candidate_id is not None
        assert result.aggregated_score > 0
        assert len(result.votes) > 0
    
    def test_get_council_summary(self):
        """経営会議概要の取得"""
        result = self.service.run_executive_decision()
        summary = self.service.get_council_summary(result)
        
        assert summary.agent_count > 0
        assert summary.candidate_count > 0
        assert summary.selected_strategy is not None
        assert summary.consensus_level in ["high", "medium", "low"]
    
    def test_get_agent_perspectives(self):
        """各エージェントの視点取得"""
        result = self.service.run_executive_decision()
        perspectives = self.service.get_agent_perspectives(result)
        
        assert len(perspectives) > 0
        for p in perspectives:
            assert "role" in p
            assert "focus" in p
            assert "top_choice" in p
    
    def test_export_to_markdown(self):
        """Markdown 出力"""
        md = self.service.export_to_markdown()
        
        assert "# 経営チームエージェント" in md
        assert "CEO" in md
        assert "CFO" in md
        assert "投票重み" in md


class TestExecutiveAgentRoles:
    """各ロールの特性テスト"""
    
    def setup_method(self):
        self.service = ExecutiveAgentService()
    
    def test_ceo_characteristics(self):
        """CEO の特性"""
        agents = self.service.get_default_agents()
        ceo = next(a for a in agents if a.role == ExecutiveRole.CEO)
        
        assert ceo.focus_area == "全社戦略・成長・持続可能性"
        assert "全社成長" in ceo.concerns
        assert ceo.vote_weight == 1.5
    
    def test_cfo_characteristics(self):
        """CFO の特性"""
        agents = self.service.get_default_agents()
        cfo = next(a for a in agents if a.role == ExecutiveRole.CFO)
        
        assert "財務" in cfo.focus_area
        assert cfo.cost_sensitivity > 0.8
        assert cfo.risk_aversion > 0.5
    
    def test_cmo_characteristics(self):
        """CMO の特性"""
        agents = self.service.get_default_agents()
        cmo = next(a for a in agents if a.role == ExecutiveRole.CMO)
        
        assert cmo.market_focus > 0.7
        assert "市場" in cmo.focus_area
    
    def test_cto_characteristics(self):
        """CTO の特性"""
        agents = self.service.get_default_agents()
        cto = next(a for a in agents if a.role == ExecutiveRole.CTO)
        
        assert cto.technology_focus > 0.7
        assert cto.innovation_weight > 0.3
    
    def test_chro_characteristics(self):
        """CHRO の特性"""
        agents = self.service.get_default_agents()
        chro = next(a for a in agents if a.role == ExecutiveRole.CHRO)
        
        assert chro.people_focus > 0.7
        assert "人材" in chro.focus_area


if __name__ == "__main__":
    pytest.main([__file__, "-v"])