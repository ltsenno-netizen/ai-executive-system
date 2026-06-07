from pydantic import BaseModel
from typing import List, Optional, Literal


class BoardMemberOpinion(BaseModel):
    member_role: str  # "financial", "brand", "risk", "org", "growth"
    preferred_option_id: str
    rationale: str
    risk_flag: bool = False


class BoardDecision(BaseModel):
    status: Literal["approved", "conditional", "rejected"]
    final_option_id: str
    final_option_label: str
    board_rationale: str
    conditions: Optional[str] = None
    member_opinions: List[BoardMemberOpinion] = []