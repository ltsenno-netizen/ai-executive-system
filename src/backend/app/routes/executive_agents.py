from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from ..models.executive_agent_model import (
    ExecutiveRole,
    ExecutiveAgentConfig,
    ExecutiveDecisionResult,
)
from ..services.executive_agent_service import ExecutiveAgentService

router = APIRouter(tags=["executive-agents"])
service = ExecutiveAgentService()


class UpdateAgentRequest(BaseModel):
    role: ExecutiveRole
    updates: Dict


class ExecutiveDecisionRequest(BaseModel):
    frontier_id: Optional[str] = None
    candidate_ids: Optional[List[str]] = None


@router.get("/executives/agents")
def get_agents():
    """経営チームのエージェント一覧を取得"""
    try:
        agents = service.get_agents()
        return {
            "count": len(agents),
            "agents": [
                {
                    "role": agent.role.value,
                    "name": agent.name,
                    "focus_area": agent.focus_area,
                    "vote_weight": agent.vote_weight,
                    "weights": {
                        "growth": agent.growth_weight,
                        "profitability": agent.profitability_weight,
                        "innovation": agent.innovation_weight,
                        "stability": agent.stability_weight,
                    },
                    "characteristics": {
                        "risk_aversion": agent.risk_aversion,
                        "cost_sensitivity": agent.cost_sensitivity,
                        "people_focus": agent.people_focus,
                        "technology_focus": agent.technology_focus,
                        "market_focus": agent.market_focus,
                    },
                    "concerns": agent.concerns,
                }
                for agent in agents
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executives/agents")
def update_agent(request: UpdateAgentRequest):
    """特定エージェントの設定を更新"""
    try:
        updated = service.update_agent(request.role, request.updates)
        return {
            "message": f"Agent {request.role.value} updated",
            "agent": {
                "role": updated.role.value,
                "name": updated.name,
                "focus_area": updated.focus_area,
                "vote_weight": updated.vote_weight,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/executives/decide")
def run_decision(request: Optional[ExecutiveDecisionRequest] = None):
    """経営会議を実行して戦略を決定"""
    try:
        result = service.run_executive_decision(
            frontier=None,
            candidates=None
        )
        
        summary = service.get_council_summary(result)
        perspectives = service.get_agent_perspectives(result)
        
        return {
            "message": "Executive decision completed",
            "decision": {
                "selected_candidate_id": result.selected_candidate_id,
                "selected_candidate_desc": result.selected_candidate_desc,
                "aggregated_score": result.aggregated_score,
                "method": result.method,
            },
            "summary": {
                "agent_count": summary.agent_count,
                "candidate_count": summary.candidate_count,
                "selected_strategy": summary.selected_strategy,
                "top_supporter": summary.top_supporter,
                "consensus_level": summary.consensus_level,
            },
            "votes": [
                {
                    "role": vote.role.value,
                    "candidate_id": vote.candidate_id,
                    "score": vote.score,
                    "rationale": vote.rationale,
                }
                for vote in result.votes
            ],
            "perspectives": perspectives,
            "vote_distribution": result.vote_distribution,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executives/council-summary")
def get_council_summary():
    """経営会議の概要を取得"""
    try:
        result = service.run_executive_decision()
        summary = service.get_council_summary(result)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executives/perspectives")
def get_perspectives():
    """各エージェントの視点を取得"""
    try:
        result = service.run_executive_decision()
        perspectives = service.get_agent_perspectives(result)
        return {
            "perspectives": perspectives,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executives/markdown")
def get_markdown():
    """経営会議設定をMarkdownで取得"""
    try:
        md = service.export_to_markdown()
        return {"markdown": md}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executives/agents/reset")
def reset_agents():
    """エージェント設定をデフォルトにリセット"""
    try:
        default_agents = service.get_default_agents()
        service.save_agents(default_agents, reason="Reset to defaults")
        return {
            "message": "Agents reset to defaults",
            "count": len(default_agents),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))