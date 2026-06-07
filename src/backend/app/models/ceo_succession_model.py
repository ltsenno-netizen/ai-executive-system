from typing import Dict, List, Optional

from pydantic import BaseModel

from .ai_ceo_model import AICeoPersona


class CeoCandidate(BaseModel):
    candidate_id: str
    persona: AICeoPersona
    strengths: List[str]
    weaknesses: List[str]
    similarity_to_current: float
    innovation_bias: float


class CeoSuccessionDecision(BaseModel):
    period: Optional[str] = None
    selected_candidate_id: str
    rationale: str
    board_votes: Dict[str, str]
    transition_notes: Optional[str] = None
