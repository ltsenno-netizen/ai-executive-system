import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from ..models.executive_agent_model import (
    ExecutiveRole,
    ExecutiveAgentConfig,
    AgentVote,
    ExecutiveDecisionResult,
    ExecutiveCouncilSummary,
)
from ..models.multi_objective_model import ParetoFrontier
from .executive_agent_engine import (
    score_candidate_for_agent,
    aggregate_votes,
    run_executive_council,
    get_default_role_weights,
    calculate_consensus_level,
)
from .multi_objective_service import MultiObjectiveService


class ExecutiveAgentService:
    """経営チームのエージェント管理と意思決定サービス"""
    
    def __init__(self):
        self.data_dir = Path("data/executive_agents")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.data_dir / "config.json"
        self.multi_objective_service = MultiObjectiveService()
    
    def get_default_agents(self) -> List[ExecutiveAgentConfig]:
        """デフォルトのエージェント設定を取得"""
        return [
            # CEO - バランスの取れた視点
            ExecutiveAgentConfig(
                role=ExecutiveRole.CEO,
                name="CEO Agent",
                growth_weight=0.30,
                profitability_weight=0.25,
                innovation_weight=0.25,
                stability_weight=0.20,
                risk_aversion=0.4,
                cost_sensitivity=0.5,
                people_focus=0.6,
                technology_focus=0.5,
                market_focus=0.5,
                vote_weight=1.5,
                focus_area="全社戦略・成長・持続可能性",
                concerns=["全社成長", "競争優位", "ステークホルダー価値"],
            ),
            # CFO - 財務・リスク重視
            ExecutiveAgentConfig(
                role=ExecutiveRole.CFO,
                name="CFO Agent",
                growth_weight=0.20,
                profitability_weight=0.40,
                innovation_weight=0.10,
                stability_weight=0.30,
                risk_aversion=0.7,
                cost_sensitivity=0.9,
                people_focus=0.3,
                technology_focus=0.3,
                market_focus=0.4,
                vote_weight=1.2,
                focus_area="財務・投資・リスク管理",
                concerns=["現金準備高", "投資対効果", "財務リスク", "コスト管理"],
            ),
            # CMO - 市場・顧客重視
            ExecutiveAgentConfig(
                role=ExecutiveRole.CMO,
                name="CMO Agent",
                growth_weight=0.35,
                profitability_weight=0.20,
                innovation_weight=0.25,
                stability_weight=0.20,
                risk_aversion=0.4,
                cost_sensitivity=0.5,
                people_focus=0.3,
                technology_focus=0.4,
                market_focus=0.9,
                vote_weight=1.0,
                focus_area="市場・顧客・ブランド",
                concerns=["市場シェア", "顧客獲得", "ブランド価値", "マーケティングROI"],
            ),
            # CTO - テクノロジー・革新重視
            ExecutiveAgentConfig(
                role=ExecutiveRole.CTO,
                name="CTO Agent",
                growth_weight=0.25,
                profitability_weight=0.15,
                innovation_weight=0.40,
                stability_weight=0.20,
                risk_aversion=0.5,
                cost_sensitivity=0.4,
                people_focus=0.4,
                technology_focus=0.9,
                market_focus=0.3,
                vote_weight=1.0,
                focus_area="技術戦略・イノベーション",
                concerns=["技術革新", "DX", "技術負債", "プラットフォーム"],
            ),
            # CHRO - 人材・組織重視
            ExecutiveAgentConfig(
                role=ExecutiveRole.CHRO,
                name="CHRO Agent",
                growth_weight=0.25,
                profitability_weight=0.20,
                innovation_weight=0.20,
                stability_weight=0.35,
                risk_aversion=0.6,
                cost_sensitivity=0.4,
                people_focus=0.9,
                technology_focus=0.3,
                market_focus=0.3,
                vote_weight=1.0,
                focus_area="人材・組織・文化",
                concerns=["人材確保", "従業員エンゲージメント", "組織文化", "Diversity"],
            ),
            # COO - 執行・オペレーション重視
            ExecutiveAgentConfig(
                role=ExecutiveRole.COO,
                name="COO Agent",
                growth_weight=0.30,
                profitability_weight=0.25,
                innovation_weight=0.15,
                stability_weight=0.30,
                risk_aversion=0.6,
                cost_sensitivity=0.7,
                people_focus=0.6,
                technology_focus=0.5,
                market_focus=0.4,
                vote_weight=1.1,
                focus_area="執行・オペレーション",
                concerns=["業務執行", "効率化", "品質管理", "サプライチェーン"],
            ),
        ]
    
    def get_agents(self) -> List[ExecutiveAgentConfig]:
        """設定からエージェントを取得（無ければデフォルト）"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [ExecutiveAgentConfig(**agent) for agent in data]
            else:
                # デフォルト設定を保存
                default_agents = self.get_default_agents()
                self.save_agents(default_agents)
                return default_agents
        except Exception:
            return self.get_default_agents()
    
    def save_agents(
        self,
        agents: List[ExecutiveAgentConfig],
        reason: Optional[str] = None
    ) -> bool:
        """エージェント設定を保存"""
        try:
            data = [
                {
                    **agent.model_dump(),
                    "last_updated": datetime.now().isoformat()
                }
                for agent in agents
            ]
            
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def update_agent(
        self,
        role: ExecutiveRole,
        updates: Dict
    ) -> ExecutiveAgentConfig:
        """特定エージェントの設定を更新"""
        agents = self.get_agents()
        
        for i, agent in enumerate(agents):
            if agent.role == role:
                # 更新適用
                for key, value in updates.items():
                    if hasattr(agent, key):
                        setattr(agent, key, value)
                break
        
        self.save_agents(agents)
        return agents[[i for i, a in enumerate(agents) if a.role == role][0]]
    
    def run_executive_decision(
        self,
        frontier: Optional[ParetoFrontier] = None,
        candidates: Optional[List] = None
    ) -> ExecutiveDecisionResult:
        """
        経営会議を実行して戦略を決定
        
        Args:
            frontier: Pareto frontier（候補はここから取得）
            candidates: 直接候補リストを指定する場合
        
        Returns:
            ExecutiveDecisionResult: 決定結果
        """
        # エージェントと重み取得
        agents = self.get_agents()
        role_weights = get_default_role_weights()
        
        # 候補取得
        if candidates is None:
            if frontier is None:
                # frontierから取得
                frontier = self.multi_objective_service.get_frontier()
                if frontier is None:
                    raise ValueError("No frontier or candidates available")
            candidates = frontier.candidates
        
        if not candidates:
            raise ValueError("No candidates to evaluate")
        
        # 経営会議実行
        result = run_executive_council(agents, candidates, role_weights)
        
        return result
    
    def get_council_summary(
        self,
        result: ExecutiveDecisionResult
    ) -> ExecutiveCouncilSummary:
        """経営会議の概要を生成"""
        # 最多支持のロール
        if result.supporting_roles:
            top_supporter = max(
                set(result.supporting_roles),
                key=result.supporting_roles.count
            )
        else:
            top_supporter = "N/A"
        
        return ExecutiveCouncilSummary(
            agent_count=len(set(v.role for v in result.votes)),
            candidate_count=len(result.vote_distribution),
            selected_strategy=result.selected_candidate_id,
            top_supporter=top_supporter,
            consensus_level=calculate_consensus_level(
                result.votes,
                get_default_role_weights()
            ),
            decision_method=result.method,
        )
    
    def get_agent_perspectives(
        self,
        result: ExecutiveDecisionResult
    ) -> List[Dict]:
        """各エージェントの視点を取得"""
        agents = self.get_agents()
        perspectives = []
        
        for agent in agents:
            agent_votes = [v for v in result.votes if v.role == agent.role]
            if agent_votes:
                top = max(agent_votes, key=lambda v: v.score)
                perspectives.append({
                    "role": agent.role.value,
                    "focus": agent.focus_area,
                    "top_choice": top.candidate_id,
                    "score": top.score,
                    "rationale": top.rationale,
                })
        
        return perspectives
    
    def export_to_markdown(self) -> str:
        """経営会議の結果をMarkdownで出力"""
        agents = self.get_agents()
        role_weights = get_default_role_weights()
        
        md = "# 経営チームエージェント\n\n"
        md += "## エージェント構成\n\n"
        
        for agent in agents:
            md += f"### {agent.role.value}\n"
            md += f"- 名前: {agent.name}\n"
            md += f"- 重点領域: {agent.focus_area}\n"
            md += f"- 投票重み: {agent.vote_weight}\n"
            md += f"- 関心事: {', '.join(agent.concerns)}\n\n"
        
        md += "## 投票重み\n\n"
        for role, weight in role_weights.items():
            md += f"- {role.value}: {weight}\n"
        
        return md