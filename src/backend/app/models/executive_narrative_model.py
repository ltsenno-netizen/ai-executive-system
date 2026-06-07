from pydantic import BaseModel
from typing import Dict, List, Optional
from .board_member_model import BoardMemberOpinion


class NarrativeSection(BaseModel):
    id: str
    title: str
    content: str
    highlights: List[str]


class DecisionRationale(BaseModel):
    option_id: str
    label: str
    pros: List[str]
    cons: List[str]
    why_chosen: str
    final_decision_actor: Optional[str] = None
    final_decision_option: Optional[str] = None
    final_decision_rationale: Optional[str] = None
    board_status: Optional[str] = None
    board_final_option: Optional[str] = None
    board_rationale: Optional[str] = None
    board_conditions: Optional[str] = None
    board_member_opinions: List[BoardMemberOpinion] = []


class ExecutiveNarrative(BaseModel):
    period: str
    summary: str
    financial_section: str
    market_section: str
    organization_section: str
    investment_section: str
    risk_section: str
    decisions_section: DecisionRationale
    next_month_focus: List[str]
    ceo_persona: Optional[Dict[str, float]] = None
    decision_commentary: Optional[str] = None


class MonthlyNarrative(BaseModel):
    month: int
    sections: List[NarrativeSection]
    sentiment: str
    key_drivers: List[str]
    risks: List[str]
    opportunities: List[str]


class AnnualNarrative(BaseModel):
    year: int
    summary: str
    major_events: List[str]
    business_unit_stories: Dict[str, str]
    strategic_shift: str
    outlook_next_year: str


class MultiYearNarrative(BaseModel):
    start_year: int
    end_year: int
    transformation_story: str
    growth_drivers: List[str]
    structural_changes: List[str]
    long_term_outlook: str
