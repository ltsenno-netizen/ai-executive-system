from pydantic import BaseModel
from typing import List

class MemberRecommendation(BaseModel):
    member_id: int
    name: str
    role: str
    priority: str  # high, medium, low
    reason: str
    suggested_action: str

class FollowUpRecommendation(BaseModel):
    date: str
    members: List[MemberRecommendation]
    summary: str