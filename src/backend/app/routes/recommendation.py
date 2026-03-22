from fastapi import APIRouter
from ..services.recommendation_service import RecommendationService

router = APIRouter()

@router.get("/recommendations/followup")
def get_followup_members():
    service = RecommendationService()
    recommendation = service.get_followup_members(top_n=3)
    return {"message": "Follow-up members recommended", "data": recommendation.dict()}