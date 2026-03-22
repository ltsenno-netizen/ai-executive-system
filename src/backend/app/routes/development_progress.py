from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict, Any
from ..services.development_progress_service import DevelopmentProgressService

router = APIRouter()

@router.get("/development/{member_id}/progress")
async def get_development_progress(member_id: int):
    """
    指定されたメンバーの育成進捗状況を取得する
    
    Args:
        member_id: メンバーのID
        
    Returns:
        DevelopmentProgress: 育成進捗状況データ
    """
    service = DevelopmentProgressService()
    progress = service.get_progress_summary(member_id)
    
    if progress is None:
        raise HTTPException(status_code=404, detail=f"Member with id {member_id} not found")
    
    return progress

@router.post("/development/{member_id}/review/{month}")
async def record_monthly_review(
    member_id: int, 
    month: int, 
    achievements: List[Dict[str, Any]] = Body(...),
    member_reflection: Optional[str] = Body(None)
):
    """
    月次レビューの記録と自動生成
    
    Args:
        member_id: メンバーのID
        month: レビュー対象の月
        achievements: 各マイルストーンの達成状況
        member_reflection: メンバーの自己振り返り（オプション）
        
    Returns:
        MonthlyReview: 生成された月次レビュー
    """
    service = DevelopmentProgressService()
    review = service.generate_monthly_review(member_id, month, achievements, member_reflection)
    
    if review is None:
        raise HTTPException(status_code=404, detail=f"Member with id {member_id} not found")
    
    return review

@router.get("/development/{member_id}/review/{month}/generate")
async def generate_monthly_review(member_id: int, month: int):
    """
    月次レビューのテンプレートを生成（実際の達成状況なしで）
    
    Args:
        member_id: メンバーのID
        month: 対象月
        
    Returns:
        dict: 月次レビューのテンプレート
    """
    service = DevelopmentProgressService()
    plan = service.development_service.generate_development_plan(member_id)
    
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Member with id {member_id} not found")
    
    # 指定月のマイルストーンを取得
    current_milestones = [m for m in plan.milestones if m.month == month]
    
    template = {
        "member_id": member_id,
        "month": month,
        "expected_milestones": [m.dict() for m in current_milestones],
        "review_template": {
            "achievements": [
                {
                    "milestone_month": m.month,
                    "milestone_title": m.title,
                    "completion_percentage": 0,
                    "completed_objectives": [],
                    "remaining_objectives": m.objectives,
                    "completed_activities": [],
                    "remaining_activities": m.activities,
                    "evaluation_results": [],
                    "notes": ""
                } for m in current_milestones
            ],
            "member_reflection": ""
        }
    }
    
    return template