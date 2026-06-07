from fastapi import APIRouter, HTTPException
from typing import List
from ..services.self_optimization_service import SelfOptimizationService
from ..models.self_optimization_model import SelfOptimizationPlan, OptimizationObjective

router = APIRouter(prefix="/self-optimization", tags=["self-optimization"])
service = SelfOptimizationService()


@router.post("/generate/{objective}")
async def generate_optimization_plan(objective: str):
    """指定された目的に基づいて自己最適化プランを生成"""
    try:
        objective_enum = OptimizationObjective(objective)
        plan = service.generate_self_optimization_plan(objective_enum)
        return {
            "message": f"Generated optimization plan for objective: {objective}",
            "plan": plan.model_dump()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid objective: {objective}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest")
async def get_latest_plan():
    """最新の最適化プランを取得"""
    try:
        plan = service.get_latest_plan()
        if plan is None:
            raise HTTPException(status_code=404, detail="No optimization plan found")
        return plan.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest/{objective}")
async def get_latest_plan_by_objective(objective: str):
    """指定された目的の最新最適化プランを取得"""
    try:
        objective_enum = OptimizationObjective(objective)
        plan = service.get_latest_plan(objective_enum)
        if plan is None:
            raise HTTPException(status_code=404, detail=f"No optimization plan found for objective: {objective}")
        return plan.model_dump()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid objective: {objective}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_plans():
    """すべての最適化プランを取得"""
    try:
        plans = service.get_all_plans()
        return {
            "count": len(plans),
            "plans": [p.model_dump() for p in plans]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
