from typing import List, Dict, Tuple
from uuid import uuid4

from ..models.executive_agent_model import (
    ExecutiveRole,
    ExecutiveAgentConfig,
    AgentVote,
    ExecutiveDecisionResult,
)
from ..models.multi_objective_model import StrategyCandidate, ParetoFrontier


def score_candidate_for_agent(
    agent: ExecutiveAgentConfig,
    candidate: StrategyCandidate
) -> AgentVote:
    """
    エージェントごとに戦略候補をスコアリング
    
    エージェントの評価関数に基づいて候補を評価し、投票を生成する。
    """
    vector = candidate.objective_vector
    
    # 基本スコア：重み付け内積
    base = (
        agent.growth_weight * vector.growth +
        agent.profitability_weight * vector.profitability +
        agent.innovation_weight * vector.innovation +
        agent.stability_weight * vector.stability
    )
    
    # リスク補正：リスク回避度が高いほどリスクペナルティ增大
    risk_index = getattr(candidate, 'risk_index', 0.5)
    risk_penalty = agent.risk_aversion * risk_index * 0.2
    
    # コスト補正：CFOなどコスト感度の低いエージェントはコストを気にする
    estimated_cost = getattr(candidate, 'estimated_cost', 0.5)
    cost_penalty = agent.cost_sensitivity * estimated_cost * 0.15
    
    # 人材・組織補正：CHROは人材への影響を重視
    people_impact = getattr(candidate, 'people_impact_score', 0.5)
    people_bonus = agent.people_focus * people_impact * 0.1
    
    # テクノロジー補正：CTOは技術革新を重視
    tech_impact = getattr(candidate, 'technology_impact_score', 0.5)
    tech_bonus = agent.technology_focus * tech_impact * 0.1
    
    # 市場補正：CMOは市場影響を重視
    market_impact = getattr(candidate, 'market_impact_score', 0.5)
    market_bonus = agent.market_focus * market_impact * 0.1
    
    # 最終スコア
    score = base - risk_penalty - cost_penalty + people_bonus + tech_bonus + market_bonus
    
    # ラショナルの生成
    rationale = (
        f"base={base:.3f}, risk_penalty={risk_penalty:.3f}, "
        f"cost_penalty={cost_penalty:.3f}, people_bonus={people_bonus:.3f}, "
        f"tech_bonus={tech_bonus:.3f}, market_bonus={market_bonus:.3f}"
    )
    
    return AgentVote(
        role=agent.role,
        candidate_id=f"{candidate.scenario_type}_{candidate.optimization_objective}",
        score=score,
        rationale=(
            f"base={base:.3f}, risk_penalty={risk_penalty:.3f}, "
            f"cost_penalty={cost_penalty:.3f}, people_bonus={people_bonus:.3f}, "
            f"tech_bonus={tech_bonus:.3f}, market_bonus={market_bonus:.3f}"
        ),
        breakdown={
            "base": base,
            "risk_penalty": risk_penalty,
            "cost_penalty": cost_penalty,
            "people_bonus": people_bonus,
            "tech_bonus": tech_bonus,
            "market_bonus": market_bonus,
            "final_score": score,
        }
    )


def aggregate_votes(
    votes: List[AgentVote],
    role_weights: Dict[ExecutiveRole, float]
) -> ExecutiveDecisionResult:
    """
    投票を集約して最終決定を生成
    
    重み付き平均で候補者をスコアリングし、勝者を選択する。
    """
    # candidate_id ごとにスコアを集約
    candidate_scores: Dict[str, float] = {}
    candidate_votes: Dict[str, List[AgentVote]] = {}
    
    for vote in votes:
        w = role_weights.get(vote.role, 1.0)
        weighted_score = vote.score * w
        
        candidate_scores[vote.candidate_id] = (
            candidate_scores.get(vote.candidate_id, 0.0) + weighted_score
        )
        
        if vote.candidate_id not in candidate_votes:
            candidate_votes[vote.candidate_id] = []
        candidate_votes[vote.candidate_id].append(vote)
    
    # 最高スコア候補を選択
    if not candidate_scores:
        raise ValueError("No votes to aggregate")
    
    selected_id, agg_score = max(candidate_scores.items(), key=lambda x: x[1])
    
    # 支持・反対ロールの特定
    supporting_roles = []
    opposing_roles = []
    avg_score = sum(candidate_scores.values()) / len(candidate_scores)
    
    for vote in votes:
        if vote.candidate_id == selected_id:
            if vote.score >= avg_score:
                supporting_roles.append(vote.role.value)
            else:
                opposing_roles.append(vote.role.value)
    
    # 投票分布の作成
    vote_distribution = {
        cid: score / len(role_weights)  # 平均化
        for cid, score in candidate_scores.items()
    }
    
    return ExecutiveDecisionResult(
        selected_candidate_id=selected_id,
        selected_candidate_desc=selected_id,
        votes=votes,
        aggregated_score=agg_score,
        method="weighted_average",
        vote_distribution=vote_distribution,
        supporting_roles=supporting_roles,
        opposing_roles=opposing_roles,
        all_scores={
            vote.candidate_id: {
                v.role.value: v.score for v in candidate_votes.get(vote.candidate_id, [])
            }
            for vote in votes
        }
    )


def run_executive_council(
    agents: List[ExecutiveAgentConfig],
    candidates: List[StrategyCandidate],
    role_weights: Dict[ExecutiveRole, float]
) -> ExecutiveDecisionResult:
    """
    経営会議を実行
    
    全エージェントが全候補を評価し、合意形成により最終戦略を選択する。
    """
    votes = []
    
    # 各エージェントが全候補を評価
    for agent in agents:
        for candidate in candidates:
            vote = score_candidate_for_agent(agent, candidate)
            votes.append(vote)
    
    # 投票を集約
    return aggregate_votes(votes, role_weights)


def get_default_role_weights() -> Dict[ExecutiveRole, float]:
    """
    デフォルトのロール重み
    
    CEOの投票力を少し強く設定（最終決定権的な位置づけ）
    """
    return {
        ExecutiveRole.CEO: 1.5,
        ExecutiveRole.CFO: 1.2,
        ExecutiveRole.CMO: 1.0,
        ExecutiveRole.CTO: 1.0,
        ExecutiveRole.CHRO: 1.0,
        ExecutiveRole.COO: 1.1,
    }


def calculate_consensus_level(
    votes: List[AgentVote],
    role_weights: Dict[ExecutiveRole, float]
) -> str:
    """
    合意度の計算
    
    全エージェントが同じ候補に投票している度高さを返す。
    """
    if not votes:
        return "low"
    
    # 候補ごとの得票数
    candidate_vote_counts: Dict[str, float] = {}
    total_weight = sum(role_weights.values())
    
    for vote in votes:
        w = role_weights.get(vote.role, 1.0)
        candidate_vote_counts[vote.candidate_id] = (
            candidate_vote_counts.get(vote.candidate_id, 0.0) + w
        )
    
    if not candidate_vote_counts:
        return "low"
    
    max_votes = max(candidate_vote_counts.values())
    consensus_ratio = max_votes / total_weight
    
    if consensus_ratio >= 0.8:
        return "high"
    elif consensus_ratio >= 0.5:
        return "medium"
    else:
        return "low"


def get_agent_perspective_summary(
    agent: ExecutiveAgentConfig,
    votes: List[AgentVote]
) -> Dict:
    """
    エージェントの視点からのサマリーを生成
    """
    agent_votes = [v for v in votes if v.role == agent.role]
    
    if not agent_votes:
        return {"role": agent.role.value, "votes": [], "top_choice": None}
    
    # 最も支持した候補
    top_vote = max(agent_votes, key=lambda v: v.score)
    
    return {
        "role": agent.role.value,
        "vote_count": len(agent_votes),
        "top_choice": top_vote.candidate_id,
        "top_score": top_vote.score,
        "average_score": sum(v.score for v in agent_votes) / len(agent_votes),
    }