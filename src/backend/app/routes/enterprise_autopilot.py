from fastapi import APIRouter, HTTPException

from ..services.enterprise_autopilot_service import EnterpriseAutopilotService

router = APIRouter(prefix="/enterprise-autopilot", tags=["enterprise-autopilot"])
service = EnterpriseAutopilotService()


@router.post("/run")
def run_autopilot_cycle():
    try:
        cycle = service.run_cycle()
        return cycle.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/latest")
def get_latest_cycle():
    cycle = service.get_latest_cycle()
    if cycle is None:
        raise HTTPException(status_code=404, detail="No autopilot cycles found")
    return cycle.model_dump()


@router.get("/history")
def get_cycle_history(limit: int = 5):
    history = service.get_cycle_history(limit)
    return [cycle.model_dump() for cycle in history]
