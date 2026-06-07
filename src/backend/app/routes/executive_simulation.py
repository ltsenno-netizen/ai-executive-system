from typing import List

from fastapi import APIRouter, HTTPException

from ..models.executive_simulation_model import ExecutiveSimulationInput, ExecutiveSimulationResult
from ..services.executive_simulation_service import ExecutiveSimulationService

router = APIRouter(prefix="/executive-simulation", tags=["executive-simulation"])
service = ExecutiveSimulationService()


@router.post("/run")
async def run_executive_simulation(sim_input: ExecutiveSimulationInput) -> ExecutiveSimulationResult:
    try:
        result = service.run_simulation(sim_input)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/latest")
async def get_latest_executive_simulation() -> ExecutiveSimulationResult:
    result = service.get_latest()
    if result is None:
        raise HTTPException(status_code=404, detail="No executive simulation found")
    return result


@router.get("/history")
async def get_executive_simulation_history(limit: int = 20) -> List[ExecutiveSimulationResult]:
    return service.list_recent(limit)


@router.get("/{simulation_id}")
async def get_executive_simulation(simulation_id: str) -> ExecutiveSimulationResult:
    result = service.get_by_id(simulation_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Executive simulation {simulation_id} not found")
    return result


@router.get("/{simulation_id}/markdown")
async def get_executive_simulation_markdown(simulation_id: str) -> dict:
    markdown = service.export_simulation_markdown(simulation_id)
    if markdown is None:
        raise HTTPException(status_code=404, detail=f"Executive simulation {simulation_id} not found")
    return {
        "simulation_id": simulation_id,
        "format": "markdown",
        "content": markdown,
    }
