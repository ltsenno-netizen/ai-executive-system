from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class ExecutiveRole(str, Enum):
    """経営チームのエージェントロール"""
    CEO = "CEO"
    CFO = "CFO"
    CMO = "CMO"
    CTO = "CTO"
    CHRO = "CHRO"
    COO = "COO"


class ExecutiveAgentConfig(BaseModel):
    """各エージェントの設定・評価関数"""
    role: ExecutiveRole
    name: str = Field(description="エージェント名")
    
    # 目的関数の重み（Corporate Intentと同構造）
    growth_weight: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="成長重視度"
    )
    profitability_weight: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="収益性重視度"
    )
    innovation_weight: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="革新性重視度"
    )
    stability_weight: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="安定性重視度"
    )
    
    # エージェント固有の特性
    risk_aversion: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="リスク回避度 (0=攻め, 1=守り)"
    )
    cost_sensitivity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="コスト感度 (CFOは高)"
    )
    people_focus: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="人材・組織への関心度 (CHROは高)"
    )
    technology_focus: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="テクノロジーへの関心度 (CTO是高)"
    )
    market_focus: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="市場・顧客への関心度 (CMO是高)"
    )
    
    # 投票重み
    vote_weight: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="経営会議での投票重み"
    )
    
    # 説明
    focus_area: str = Field(
        default="",
        description="担当領域の説明"
    )
    concerns: List[str] = Field(
        default_factory=list,
        description="主要な関心事"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "CFO",
                "name": "CFO Agent",
                "growth_weight": 0.2,
                "profitability_weight": 0.4,
                "innovation_weight": 0.1,
                "stability_weight": 0.3,
                "risk_aversion": 0.7,
                "cost_sensitivity": 0.9,
                "people_focus": 0.3,
                "vote_weight": 1.2,
                "focus_area": "財務・投資・リスク管理",
                "concerns": ["現金準備高", "投資対効果", "財務リスク"]
            }
        }


class AgentVote(BaseModel):
    """エージェントの投票"""
    role: ExecutiveRole
    candidate_id: str
    score: float
    rationale: str
    breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="スコア計算の詳細内訳"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="投票時刻"
    )


class ExecutiveDecisionResult(BaseModel):
    """経営会議の決定結果"""
    selected_candidate_id: Optional[str] = Field(None, description="Selected candidate identifier")
    selected_candidate_desc: Optional[str] = Field(None, description="Description of the selected candidate")
    votes: List[AgentVote] = Field(default_factory=list)
    aggregated_score: float = Field(default=0.0)
    method: str = Field(default="legacy")  # "weighted_average", "majority", "consensus"
    decision_summary: Optional[str] = Field(None, description="Legacy decision summary")
    
    # 投票分析
    vote_distribution: Dict[str, float] = Field(
        default_factory=dict,
        description="候補者ごとの得票分布"
    )
    supporting_roles: List[str] = Field(
        default_factory=list,
        description="支持したロール一覧"
    )
    opposing_roles: List[str] = Field(
        default_factory=list,
        description="反対したロール一覧"
    )
    
    # 詳細
    all_scores: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="全エージェント×全候補のスコア行列"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="決定時刻"
    )


class ExecutiveCouncilSummary(BaseModel):
    """経営会議の概要"""
    agent_count: int
    candidate_count: int
    selected_strategy: str
    top_supporter: str
    consensus_level: str  # "high", "medium", "low"
    decision_method: str