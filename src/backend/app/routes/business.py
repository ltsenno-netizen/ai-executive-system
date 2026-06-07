from fastapi import APIRouter, HTTPException
from ..services.business_service import BusinessService

router = APIRouter()

@router.get('/business/horipro')
def get_horipro_business_model():
    service = BusinessService()
    try:
        business = service.load_business_model()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return business.dict()
