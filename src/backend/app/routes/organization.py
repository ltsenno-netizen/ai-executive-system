from fastapi import APIRouter, HTTPException
from ..services.organization_service import OrganizationService

router = APIRouter()

@router.get('/organization/horipro')
def get_horipro_organization_model():
    service = OrganizationService()
    try:
        organization = service.load_organization_model()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return organization.model_dump()
