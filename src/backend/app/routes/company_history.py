from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from ..models.company_history_model import LeadershipEvent, AnnualReport, CompanyHistory
from ..services.company_history_service import CompanyHistoryService

router = APIRouter(prefix="/history", tags=["company_history"])
service = CompanyHistoryService()

@router.get("/annual/latest", response_model=AnnualReport)
async def get_latest_annual_history():
    """Get the latest annual history report."""
    report = service.get_latest_annual_history()
    if report is None:
        raise HTTPException(status_code=404, detail="No annual history found")
    return report

@router.get("/annual/{year}", response_model=AnnualReport)
async def get_annual_history(year: int):
    """Get annual history report for a specific year."""
    report = service.get_annual_history(year)
    if report is None:
        raise HTTPException(status_code=404, detail="Annual history not found")
    return report

@router.get("/timeline", response_model=CompanyHistory)
async def get_leadership_timeline():
    """Get the complete leadership timeline."""
    try:
        return service.generate_timeline()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-annual/{year}")
async def generate_annual_history(year: int):
    """Generate annual history report for a specific year."""
    try:
        report = service.generate_annual_history(year)
        return {"message": f"Annual history generated for {year}", "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-timeline")
async def generate_leadership_timeline():
    """Generate the leadership timeline."""
    try:
        timeline = service.generate_timeline()
        return {"message": "Leadership timeline generated", "timeline": timeline}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))