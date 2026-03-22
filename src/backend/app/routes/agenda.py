from fastapi import APIRouter
from ..services.agenda_service import AgendaService

router = APIRouter()

@router.get("/agenda/weekly")
def get_weekly_agenda():
    service = AgendaService()
    agenda = service.generate_weekly_agenda()
    return {"message": "Weekly agenda generated", "data": agenda.dict()}