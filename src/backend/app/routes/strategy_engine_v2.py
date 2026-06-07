from fastapi import APIRouter, HTTPException
from ..services.strategy_engine_v2_service import StrategyEngineV2Service

router = APIRouter(prefix="/strategy/v2", tags=["strategy-v2"])
service = StrategyEngineV2Service()


@router.post("/run/{scenario_type}")
def run_strategy_for_scenario(scenario_type: str):
    try:
        report = service.run_strategy_for_scenario_type(scenario_type)
        return report.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/latest/{scenario_type}")
def get_latest_strategy_report(scenario_type: str):
    report = service.get_report(scenario_type)
    if report is None:
        raise HTTPException(status_code=404, detail=f"No strategy report found for scenario {scenario_type}")
    return report.model_dump()


@router.get("/latest")
def get_latest_strategy_report_overall():
    report = service.get_latest_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No strategy reports available")
    return report.model_dump()


@router.get("/markdown/{scenario_type}")
def get_strategy_report_markdown(scenario_type: str):
    markdown = service.export_report_markdown(scenario_type)
    if markdown is None:
        raise HTTPException(status_code=404, detail=f"Report not found for scenario {scenario_type}")
    return {"scenario_type": scenario_type, "markdown": markdown}
