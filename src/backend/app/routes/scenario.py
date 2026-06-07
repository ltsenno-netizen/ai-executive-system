from fastapi import APIRouter, HTTPException
from typing import List
from ..services.scenario_service import ScenarioService
from ..models.scenario_model import ScenarioResult

router = APIRouter(prefix="/scenarios", tags=["scenarios"])
service = ScenarioService()

@router.post("/run")
async def run_scenarios():
    \"\"\"全シナリオを実行\"\"\"
    try:
        results = service.run_all_scenarios()
        return {"message": f"Executed {len(results)} scenarios", "results": [r.scenario_type.value for r in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest")
async def get_latest_scenarios():
    \"\"\"最新のシナリオ結果を取得\"\"\"
    try:
        results = service.get_all_scenario_results()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scenario_type}")
async def get_scenario(scenario_type: str):
    \"\"\"指定シナリオの結果を取得\"\"\"
    try:
        result = service.get_scenario_result(scenario_type)
        if result is None:
            raise HTTPException(status_code=404, detail="Scenario not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
