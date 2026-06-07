from typing import Dict, List, Optional
from pydantic import BaseModel

class ExecutiveRole(BaseModel):
    role_id: str
    title: str
    responsibilities: List[str]
    required_skills: List[str]

class ExecutiveCandidate(BaseModel):
    candidate_id: str
    name: str
    current_role: str
    experience_years: int
    skills: List[str]
    performance_rating: float
    succession_readiness: float

class ExecutiveSuccessionDecision(BaseModel):
    period: Optional[str] = None
    role_id: str
    selected_candidate_id: str
    rationale: str
    board_votes: Dict[str, str]
    transition_plan: Optional[str] = None