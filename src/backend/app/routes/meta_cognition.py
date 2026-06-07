from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models.meta_cognition_model import MetaCognitionReport
from ..services.meta_cognition_service import MetaCognitionService

router = APIRouter(tags=["meta-cognition"])
_service: Optional[MetaCognitionService] = None


def get_service() -> MetaCognitionService:
    global _service
    if _service is None:
        _service = MetaCognitionService()
    return _service


class MarkdownResponse(BaseModel):
    markdown: str


@router.post("/meta-cognition/run", response_model=MetaCognitionReport)
def run_meta_cognition_assessment():
    try:
        service = get_service()
        return service.run_assessment()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/meta-cognition/latest", response_model=MetaCognitionReport)
def get_latest_meta_cognition_report():
    service = get_service()
    report = service.get_latest()
    if report is None:
        raise HTTPException(status_code=404, detail="No meta-cognition report available")
    return report


@router.get("/meta-cognition/history", response_model=List[MetaCognitionReport])
def get_meta_cognition_history():
    service = get_service()
    return service.get_history()


@router.get("/meta-cognition/markdown/{report_id}", response_model=MarkdownResponse)
def get_meta_cognition_markdown(report_id: str):
    service = get_service()
    markdown = service.export_report_markdown(report_id)
    if markdown is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"markdown": markdown}
