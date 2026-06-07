from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal
from .board_member_model import BoardMemberOpinion


class MeetingAgendaItem(BaseModel):
    id: str
    category: str
    title: str
    summary: str
    ai_recommendation: str
    impact: Dict[str, float]


class MeetingDecision(BaseModel):
    agenda_id: str
    decision: str
    comment: str
    applied_effect: Dict[str, float]


class ExecutiveAgent(BaseModel):
    role: str
    focus: str
    opening_statement: str
    recommendation: str
    concerns: List[str]


class ExecutiveDebateSummary(BaseModel):
    opening_statements: List[ExecutiveAgent]
    cross_discussion: List[str]
    consensus: str
    divergence: List[str]


class DecisionOption(BaseModel):
    id: str
    label: str
    actions: List[str]
    pros: List[str]
    cons: List[str]
    risk_level: Optional[str] = None
    expected_impact_score: Optional[float] = None
    growth_score: Optional[float] = None
    brand_impact: Optional[float] = None
    short_term_profit: Optional[float] = None
    long_term_value: Optional[float] = None


class BoardDecision(BaseModel):
    status: Literal['approved', 'conditional', 'rejected']
    final_option_id: str
    final_option_label: str
    board_rationale: str
    conditions: Optional[str] = None
    member_opinions: List[BoardMemberOpinion] = []


class MeetingMinutes(BaseModel):
    summary: str
    discussion_highlights: List[str]
    decisions_recorded: List[Dict[str, object]]
    ceo_comment: str


class ExecutiveMeetingState(BaseModel):
    month: int
    agenda: List[MeetingAgendaItem]
    decisions: List[MeetingDecision]
    next_month_projection: Dict[str, float]
    executive_agents: List[ExecutiveAgent] = Field(default_factory=list)
    debate_summary: ExecutiveDebateSummary | None = None
    decision_options: List[DecisionOption] = Field(default_factory=list)
    meeting_minutes: MeetingMinutes | None = None
    selected_option_id: str | None = None
    ceo_comment: str | None = None
    ceo_selected_option_id: str | None = None
    ceo_selected_option_label: str | None = None
    ceo_decision_rationale: str | None = None
    ceo_persona: Optional[Dict[str, float]] = None
    board_decision: Optional[BoardDecision] = None
    decision_actor: Optional[Literal['User', 'AI CEO + Board']] = None
