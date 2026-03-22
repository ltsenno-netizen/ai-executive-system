from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from ..services.leadership.simulation_service import LeadershipSimulationService
from ..models.leadership.simulation import LeadershipDecision

class StartSimulationRequest(BaseModel):
    user_id: str
    scenario_type: Optional[str] = "team_conflict"
    difficulty: Optional[str] = "medium"

router = APIRouter()

@router.post("/leadership/simulation/start")
async def start_simulation(request: StartSimulationRequest):
    """
    新しいリーダーシップシミュレーションを開始
    
    Args:
        request: シミュレーション開始リクエスト
        
    Returns:
        dict: シミュレーション情報
    """
    service = LeadershipSimulationService()
    simulation = service.create_simulation(request.user_id, request.difficulty)
    
    return {
        "simulation_id": simulation.simulation_id,
        "project": {
            "name": simulation.project.name,
            "description": simulation.project.description,
            "duration_weeks": simulation.project.duration_weeks,
            "objectives": simulation.project.objectives
        },
        "team": [
            {
                "name": member.name,
                "role": member.role,
                "personality": member.personality,
                "leadership_style": member.leadership_style
            } for member in simulation.team
        ],
        "message": "リーダーシップシミュレーションを開始しました。最初のトラブルが発生するまでプロジェクトが進みます。"
    }

@router.get("/leadership/simulation/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """
    シミュレーションの現在の状態を取得
    
    Args:
        simulation_id: シミュレーションID
        
    Returns:
        dict: 現在の状態
    """
    # TODO: 実際のデータベースから取得
    service = LeadershipSimulationService()
    
    # モックデータ
    return {
        "simulation_id": simulation_id,
        "status": "active",
        "current_scenario": None,
        "decisions_made": 0,
        "remaining_scenarios": 3,
        "progress_percentage": 0
    }

@router.get("/leadership/simulation/{simulation_id}/next-scenario")
async def get_next_scenario(simulation_id: str):
    """
    次のトラブルシナリオを取得
    
    Args:
        simulation_id: シミュレーションID
        
    Returns:
        dict: シナリオ情報とメンバーの反応
    """
    service = LeadershipSimulationService()
    
    # モックシミュレーション作成
    simulation = service.create_simulation("test_user")
    scenario = service.get_next_scenario(simulation)
    
    if not scenario:
        return {"message": "すべてのシナリオが完了しました"}
    
    reactions = service.generate_member_reactions(scenario, simulation.team)
    
    return {
        "scenario": {
            "scenario_id": scenario.scenario_id,
            "type": scenario.type,
            "severity": scenario.severity,
            "description": scenario.description,
            "impact": scenario.impact,
            "possible_responses": scenario.possible_responses
        },
        "member_reactions": [
            {
                "member_name": next((m.name for m in simulation.team if m.member_id == r.member_id), "Unknown"),
                "reaction_type": r.reaction_type,
                "response": r.response,
                "emotional_state": r.emotional_state,
                "suggested_action": r.suggested_action
            } for r in reactions
        ],
        "message": "トラブルが発生しました。どのように対応しますか？"
    }

@router.post("/leadership/simulation/{simulation_id}/decide")
async def make_decision(
    simulation_id: str,
    decision: LeadershipDecision
):
    """
    判断を下す
    
    Args:
        simulation_id: シミュレーションID
        decision: 判断内容
        
    Returns:
        dict: 判断の評価結果
    """
    service = LeadershipSimulationService()
    
    # モックシミュレーション作成
    simulation = service.create_simulation("test_user")
    scenario = service.get_next_scenario(simulation)
    
    if not scenario:
        raise HTTPException(status_code=400, detail="有効なシナリオが見つかりません")
    
    # 評価を実行
    evaluation = service.evaluate_decision(decision, scenario, simulation.team)
    
    return {
        "evaluation": {
            "scores": evaluation.scores,
            "strengths": evaluation.strengths,
            "weaknesses": evaluation.weaknesses,
            "recommendations": evaluation.recommendations,
            "leadership_style": evaluation.leadership_style_assessment,
            "development_areas": evaluation.development_areas
        },
        "feedback": {
            "overall_assessment": f"今回の判断は{evaluation.scores['overall']:.1f}点です。",
            "key_learning": "リーダーシップは状況に応じた柔軟な対応が重要です。",
            "next_steps": "次のシナリオではチームの意見をより重視してください。"
        }
    }

@router.get("/leadership/simulation/{simulation_id}/complete")
async def complete_simulation(simulation_id: str):
    """
    シミュレーションを完了し、最終評価を取得
    
    Args:
        simulation_id: シミュレーションID
        
    Returns:
        dict: 最終結果
    """
    return {
        "simulation_id": simulation_id,
        "final_score": 85.5,
        "completion_time": "2026-03-22T10:30:00Z",
        "rank": "優秀",
        "certificate": "AIリーダーシップシミュレーション修了証",
        "summary": {
            "total_scenarios": 5,
            "decisions_made": 5,
            "average_score": 85.5,
            "leadership_style": "民主的リーダーシップ",
            "strengths": ["チーム指向", "状況判断力", "コミュニケーション"],
            "development_areas": ["危機管理", "意思決定の迅速化"]
        },
        "recommendations": [
            "次期マネージャー候補として適性あり",
            "リーダーシップ研修の継続を推奨",
            "実務でのチームリーダー経験を積むことを推奨"
        ]
    }