from fastapi import APIRouter, HTTPException
from ..services.talent_management_engine import TalentManagementEngine

router = APIRouter()
engine = TalentManagementEngine()

@router.get("/api/talent/mission")
async def get_mission():
    """部門ミッションと主要KPIを返す"""
    try:
        mission = engine.load_missions()
        return mission
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/api/talent/roles")
async def get_roles():
    """役割定義一覧を返す"""
    try:
        roles = engine.load_role_definitions()
        return roles
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/api/talent/task-templates")
async def get_task_templates():
    """タスクテンプレ一覧を返す"""
    try:
        templates = engine.load_task_templates()
        return templates
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/api/talent/task")
async def create_task(data: dict):
    """タスクインスタンスを生成"""
    try:
        template_id = data.get("template_id")
        related_project = data.get("related_project")

        if not template_id:
            raise HTTPException(status_code=400, detail="template_id is required")

        task = engine.instantiate_task(template_id, related_project)
        return {
            "message": "Task created successfully",
            "task": task
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/api/talent/task/{task_id}/assign")
async def assign_task(task_id: str, data: dict):
    """タスクをメンバーに割当"""
    try:
        member_id = data.get("member_id")

        if not member_id:
            raise HTTPException(status_code=400, detail="member_id is required")

        success = engine.assign_task(task_id, member_id)
        if not success:
            raise HTTPException(status_code=400, detail="Assignment failed")

        return {"message": "Task assigned successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/api/talent/incident/{scenario_id}/create")
async def create_incident(scenario_id: str):
    """インシデントを生成"""
    try:
        incident = engine.create_incident(scenario_id)
        return {
            "message": "Incident created successfully",
            "incident": incident
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/api/talent/simulate")
async def run_simulation(data: dict):
    """シミュレーションを実行"""
    try:
        days = data.get("days", 1)
        seed = data.get("seed")

        if not isinstance(days, int) or days < 1:
            raise HTTPException(status_code=400, detail="days must be a positive integer")

        report = engine.run_simulation_step(days, seed)

        return {
            "days_simulated": report.days_simulated,
            "tasks_completed": report.tasks_completed,
            "incidents_occurred": report.incidents_occurred,
            "kpi_changes": report.kpi_changes,
            "pl_impact": report.pl_impact
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")