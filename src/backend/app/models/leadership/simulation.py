from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class VirtualTeamMember(BaseModel):
    """仮想チームメンバー"""
    member_id: str
    name: str
    role: str
    personality: str  # 内向的/外向的, 協調的/競争的, etc.
    skills: Dict[str, float]  # skill_name -> proficiency (0-1)
    leadership_style: str
    stress_tolerance: float  # 0-1
    communication_style: str

class VirtualProject(BaseModel):
    """仮想プロジェクト"""
    project_id: str
    name: str
    description: str
    duration_weeks: int
    complexity: str  # low/medium/high
    risk_level: str  # low/medium/high
    objectives: List[str]
    milestones: List[Dict[str, Any]]

class TroubleScenario(BaseModel):
    """トラブルシナリオ"""
    scenario_id: str
    type: str  # technical, interpersonal, resource, deadline, etc.
    severity: str  # minor/major/critical
    description: str
    impact: str
    possible_responses: List[str]
    correct_approach: str

class MemberReaction(BaseModel):
    """メンバーの反応"""
    member_id: str
    reaction_type: str  # positive/negative/neutral
    response: str
    emotional_state: str
    suggested_action: str

class LeadershipDecision(BaseModel):
    """リーダーシップ判断"""
    decision_id: str
    scenario_id: str
    decision_maker: str  # user or AI
    chosen_action: str
    reasoning: str
    timestamp: datetime

class SimulationResult(BaseModel):
    """シミュレーション結果"""
    simulation_id: str
    user_id: str
    project: VirtualProject
    team: List[VirtualTeamMember]
    scenarios: List[TroubleScenario]
    decisions: List[LeadershipDecision]
    final_score: float
    feedback: Dict[str, Any]
    completed_at: datetime

class LeadershipEvaluation(BaseModel):
    """リーダーシップ評価"""
    evaluation_id: str
    simulation_id: str
    evaluated_by: str  # AI or human
    scores: Dict[str, float]  # category -> score
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    leadership_style_assessment: str
    development_areas: List[str]