from fastapi import APIRouter, HTTPException
from ..services.oneonone_service import OneOnOneService

router = APIRouter()

@router.get("/oneonone/{member_id}")
def get_oneonone_preparation(member_id: int):
    service = OneOnOneService()
    result = service.prepare_oneonone(member_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "1on1 preparation data generated", "data": result}