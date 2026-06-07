from fastapi import APIRouter, HTTPException
from typing import Dict

from ..services.scenario_simulation_service import ScenarioSimulationService

router = APIRouter(prefix="/scenario-simulations", tags=["scenario-simulations"])
service = ScenarioSimulationService()

@router.post("/run")
async def run_scenario_simulations() -> Dict[str, object]:
    try:
        results = service.run_all_simulations()
        return {
            "message": f"Executed {len(results)} future scenario simulations",
            "results": [result.model_dump() for result in results],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest")
async def get_latest_scenario_simulations() -> Dict[str, object]:
    try:
        results = service.get_all_simulation_results()
        return {"simulations": [result.model_dump() for result in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview")
async def get_scenario_simulation_preview() -> Dict[str, object]:
    try:
        preview = service.get_latest_simulation_preview()
        if preview is None:
            raise HTTPException(status_code=404, detail="No scenario simulation preview available")
        return preview
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scenario_type}")
async def get_scenario_simulation(scenario_type: str) -> Dict[str, object]:
    try:
        result = service.get_simulation_result(scenario_type)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Scenario simulation '{scenario_type}' not found")
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
