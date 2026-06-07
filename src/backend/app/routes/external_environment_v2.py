from fastapi import APIRouter, HTTPException
from typing import Optional

from ..services.external_environment_service_v2 import ExternalEnvironmentServiceV2

router = APIRouter()
service = ExternalEnvironmentServiceV2()


@router.get('/environment/latest')
def get_latest_environment():
    try:
        environment = service.get_latest_environment()
        if environment is None:
            raise HTTPException(status_code=404, detail='No environment data available')
        return environment.model_dump()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/environment/{period}')
def get_environment(period: str):
    try:
        environment = service.get_environment(period)
        if environment is None:
            raise HTTPException(status_code=404, detail=f'Environment not found for period {period}')
        return environment.model_dump()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
