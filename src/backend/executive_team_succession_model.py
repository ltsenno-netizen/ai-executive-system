from enum import Enum
from typing import Dict, List
from pydantic import BaseModel


class ExecutiveRole(str, Enum):
    CFO = "cfo"
    COO = "coo"
    CMO = "cmo"
    CHRO = "chro"


class ExecutivePersona(BaseModel):
    role: ExecutiveRole
    financial_focus: float
    operational_focus: float
    brand_focus: float
    people_focus: float
    risk_tolerance: float
    innovation_bias: float


class ExecutiveCandidate(BaseModel):
    candidate_id: str
    role: ExecutiveRole
    persona: ExecutivePersona
    strengths: List[str]
    weaknesses: List[str]
    similarity_to_current: float
    innovation_bias: float


class ExecutiveSuccessionDecision(BaseModel):
    role: ExecutiveRole
    selected_candidate_id: str
    rationale: str
    board_votes: Dict[str, str]
    period: str