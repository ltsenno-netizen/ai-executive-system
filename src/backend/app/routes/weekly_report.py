from fastapi import APIRouter
from ..services.weekly_report_service import WeeklyReportService

router = APIRouter()

@router.get("/weekly-report")
def weekly_report():
    service = WeeklyReportService()
    report = service.generate_weekly_report()
    return {"message": "Weekly report generated", "data": report}