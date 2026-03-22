from fastapi import APIRouter, HTTPException
from typing import Optional
from ..services.development_service import DevelopmentService

router = APIRouter()

@router.get("/development/{member_id}")
async def get_development_plan(member_id: int):
    """
    指定されたメンバーの育成計画を取得する
    
    Args:
        member_id: メンバーのID
        
    Returns:
        DevelopmentPlan: 育成計画データ
    """
    service = DevelopmentService()
    plan = service.generate_development_plan(member_id)
    
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Member with id {member_id} not found")
    
    return plan