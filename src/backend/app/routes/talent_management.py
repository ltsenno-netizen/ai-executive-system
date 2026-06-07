from fastapi import APIRouter, HTTPException
from ..services.talent_management_service import TalentManagementService
from ..models.talent_management import MemberProfile

router = APIRouter()
service = TalentManagementService()

@router.get("/api/talent/units")
async def get_units():
    """全ユニット定義を返す"""
    try:
        units = service.load_units()
        return units
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/api/talent/unit/{unit_name}/inbasket")
async def get_unit_inbasket(unit_name: str, n: int = 5):
    """指定ユニット向けのインバスケットを返す"""
    try:
        inbasket = service.generate_inbasket_for_unit(unit_name, n)
        return {"unit_name": unit_name, "inbasket": inbasket}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/api/talent/member")
async def create_member(member: MemberProfile):
    """仮想メンバー作成"""
    try:
        success = service.create_member(member)
        if not success:
            raise HTTPException(status_code=400, detail="Member ID already exists")
        return {"message": "Member created successfully", "member_id": member.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/api/talent/assign")
async def assign_task(data: dict):
    """タスクをメンバーに割当"""
    try:
        task_id = data.get("task_id")
        member_id = data.get("member_id")

        if not task_id or not member_id:
            raise HTTPException(status_code=400, detail="task_id and member_id are required")

        success = service.assign_task_to_member(task_id, member_id)
        if not success:
            raise HTTPException(status_code=400, detail="Assignment failed")

        return {"message": "Task assigned successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/api/talent/simulate")
async def simulate_time(data: dict):
    """時間を進めてシミュレーションを実行"""
    try:
        months = data.get("months", 1)
        if not isinstance(months, int) or months < 1:
            raise HTTPException(status_code=400, detail="months must be a positive integer")

        result = service.simulate_time_advance(months)

        return {
            "months_simulated": months,
            "completed_tasks": result.completed_tasks,
            "new_incidents": result.new_incidents,
            "kpi_changes": result.kpi_changes
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")