from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional

from ..services.executive_meeting_service import ExecutiveMeetingService

router = APIRouter()
service = ExecutiveMeetingService()


class MeetingDecisionRequest(BaseModel):
    agenda_id: str
    decision: str
    comment: str


class MeetingRequest(BaseModel):
    month: int
    decisions: List[MeetingDecisionRequest] = []


class DecisionOptionRequest(BaseModel):
    month: int
    option_id: str
    ceo_comment: Optional[str] = None


@router.get('/meeting/agenda')
def get_meeting_agenda(month: int = Query(..., ge=1, le=12)):
    try:
        agenda = service.build_meeting_agenda(month)
        return [item.model_dump() for item in agenda]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post('/meeting/decide')
def post_meeting_decisions(request: MeetingRequest):
    try:
        decisions = [decision.model_dump() for decision in request.decisions]
        state = service.simulate_executive_meeting(request.month, decisions)
        return state.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/meeting/options')
def get_meeting_options(month: int = Query(..., ge=1, le=12)):
    try:
        agenda = service.build_meeting_agenda(month)
        options = service.generate_decision_options(agenda)
        return [option.model_dump() for option in options]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/meeting/debate')
def get_meeting_debate(month: int = Query(..., ge=1, le=12)):
    try:
        agenda = service.build_meeting_agenda(month)
        agents = service.build_executive_agents(agenda)
        debate = service.run_executive_debate(agenda, agents)
        return debate.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post('/meeting/decision')
def post_meeting_decision(request: DecisionOptionRequest):
    try:
        state = service.simulate_executive_meeting_with_option(
            request.month,
            request.option_id,
            request.ceo_comment,
        )
        return state.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/meeting/state')
def get_meeting_state(month: int = Query(..., ge=1, le=12)):
    try:
        state = service.load_latest_state_for_month(month)
        return state.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
