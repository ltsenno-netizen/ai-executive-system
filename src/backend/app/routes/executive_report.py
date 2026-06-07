from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict

from ..services.executive_report_service import ExecutiveReportService

router = APIRouter()
service = ExecutiveReportService()


@router.get('/reports/latest')
def get_latest_report():
    try:
        reports = service.list_reports(limit=1)
        if not reports:
            raise FileNotFoundError('No reports available')
        report = reports[0]
        content = service.get_report(report['period'])
        return {
            'period': report['period'],
            'title': report['title'],
            'content': content,
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/reports/{year}/{month}')
def get_report_by_period(year: int, month: int):
    try:
        period = f"{year:04d}-{month:02d}"
        content = service.get_report(period)
        reports = service.list_reports(limit=1)
        title = next((item['title'] for item in reports if item['period'] == period), f"月次経営レポート {year}年{month}月")
        return {
            'period': period,
            'title': title,
            'content': content,
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/reports/history')
def get_report_history(limit: int = Query(6, ge=1, le=12)) -> List[Dict[str, str]]:
    try:
        return service.list_reports(limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
