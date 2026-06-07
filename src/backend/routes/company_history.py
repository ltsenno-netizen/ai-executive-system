from fastapi import APIRouter, HTTPException
from ..services.company_history_service import CompanyHistoryService

router = APIRouter()
history_service = CompanyHistoryService()


@router.get("/history/annual/latest")
async def get_latest_annual_report():
    """最新の年次レポートを取得"""
    report = history_service.get_latest_annual_report()
    if not report:
        raise HTTPException(status_code=404, detail="No annual reports found")
    return report


@router.get("/history/annual/{year}")
async def get_annual_report(year: int):
    """指定年の年次レポートを取得"""
    report = history_service.get_annual_report(year)
    if not report:
        raise HTTPException(status_code=404, detail=f"No annual report found for year {year}")
    return report


@router.get("/history/timeline")
async def get_company_timeline():
    """企業の完全なタイムラインを取得"""
    timeline = history_service.generate_timeline()
    return timeline