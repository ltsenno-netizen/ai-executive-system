from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal

from .mid_term_plan_model import MidTermPlanSummary
from .board_member_model import BoardMemberOpinion
from .culture_model import CultureSummary
from .corporate_memory_model import CorporateMemorySummary
from .multi_company_comparative_model import MultiCompanyComparisonSummary
from .strategy_engine_v2_model import StrategyV2Summary
from .enterprise_autopilot_model import AutopilotSummary


class CeoPersonaSummary(BaseModel):
    aggressiveness: float
    risk_tolerance: float
    brand_priority: float
    short_term_focus: float
    long_term_focus: float


class CeoSuccessionSummary(BaseModel):
    last_succession_period: str
    new_ceo_persona: CeoPersonaSummary
    rationale: str


class ReportSummary(BaseModel):
    period: str
    title: str
    summary: str


class ExecutivePLSummary(BaseModel):
    month: int
    revenue: float
    cost: float
    profit: float
    profit_margin: float
    cash_balance: float


class ExecutiveKPISummary(BaseModel):
    month: int
    kpis: Dict[str, float]


class ExecutiveOpsSummary(BaseModel):
    month: int
    department_load: Dict[str, float]
    active_tasks: int
    incidents: int


class ExecutiveIssueSummary(BaseModel):
    month: int
    issues: List[Dict[str, object]]


class ExecutivePortfolioSummary(BaseModel):
    month: int
    invest_targets: List[str]
    reduce_targets: List[str]
    exit_candidates: List[str]
    new_business_candidates: List[str]
    total_required_budget: float
    remaining_budget: float


class ExecutiveMeetingTimelineItem(BaseModel):
    month: int
    selected_option_id: Optional[str] = None
    selected_option_label: Optional[str] = None
    approved_count: int
    rejected_count: int
    modified_count: int
    held_count: int
    next_month_highlight: str
    meeting_risk_level: Optional[str] = None


class ExecutiveMeetingSummary(BaseModel):
    month: int
    agenda_count: int
    approved_count: int
    rejected_count: int
    modified_count: int
    held_count: int
    next_month_highlight: str
    selected_option_id: Optional[str] = None
    selected_option_label: Optional[str] = None
    ceo_selected_option_label: Optional[str] = None
    ceo_decision_rationale: Optional[str] = None
    decision_actor: Optional[Literal['User', 'AI CEO', 'AI CEO + Board']] = None
    meeting_risk_level: Optional[str] = None
    board_status: Optional[str] = None
    board_final_option_label: Optional[str] = None
    board_rationale: Optional[str] = None
    board_conditions: Optional[str] = None
    board_member_opinions: List[BoardMemberOpinion] = []


class QuarterlyReviewSummary(BaseModel):
    quarter: str
    revenue_total: float
    profit_total: float
    board_status: str
    next_quarter_focus: List[str]


class ExecutiveNarrativeSummary(BaseModel):
    story_highlights: List[str]
    sentiment: str
    key_drivers: List[str]
    risks: List[str]
    opportunities: List[str]


class ExecutiveImprovementSummary(BaseModel):
    month: int
    executed_actions: List[Dict[str, object]]
    updated_priorities: Dict[str, float]


class ExecutiveCustomerSegmentSummary(BaseModel):
    name: str
    estimated_customers: float
    avg_spend: float
    purchase_frequency: float
    linked_business_units: List[str]


class ExecutiveCustomerSummary(BaseModel):
    segments: List[ExecutiveCustomerSegmentSummary]


class ExecutiveOrganizationUnitSummary(BaseModel):
    name: str
    headcount: int
    workload_index: float
    skill_highlights: List[str]
    open_positions: int
    monthly_personnel_cost: float


class ExecutiveOrganizationSummary(BaseModel):
    units: List[ExecutiveOrganizationUnitSummary]


class ExecutiveFinancialSummary(BaseModel):
    cash_reserves: float
    free_cash_flow: float
    short_term_debt: float
    long_term_debt: float
    monthly_debt_service: float
    available_credit_line: float
    committed_capex: float
    liquidity_buffer_months: float
    investment_requests_pending: List[Dict[str, object]]
    emergency_playbook: Optional[Dict[str, object]] = None


class ExecutiveExecutionSummary(BaseModel):
    capacity: float
    load: float
    efficiency: float
    execution_capacity_score: float
    forecast: Optional[List[Dict[str, object]]] = None


class ExecutiveScenarioSimulationSummary(BaseModel):
    scenario_type: str
    description: str
    confidence: float
    risk_assessment: str
    opportunity_assessment: str
    financial_impact_summary: Dict[str, float]
    key_impacts: Dict[str, object]
    strategic_implications: List[str]
    contingency_recommendations: List[str]


class ExecutiveSimulationSummary(BaseModel):
    last_simulation_id: str
    scenario_type: str
    consensus_level: float
    approved: bool
    key_roles_opposed: List[str]
    last_run_at: datetime


class ExecutiveMarketSegmentSummary(BaseModel):
    id: str
    name: str
    current_index: float
    growth_rate: float
    volatility: float


class ExecutiveMarketEventSummary(BaseModel):
    id: str
    type: str
    impact_map: Dict[str, float]
    duration_months: int
    source: str
    notes: str


class ExecutiveMarketSummary(BaseModel):
    segments: List[ExecutiveMarketSegmentSummary]
    active_events: List[ExecutiveMarketEventSummary]
    scenario_results_preview: Optional[Dict[str, object]] = None
    scenario_simulation_summary: Optional[ExecutiveScenarioSimulationSummary] = None


class ExternalEnvironmentSummary(BaseModel):
    economic: float
    competitor_pressure: float
    shock_summary: List[str]


class ExecutiveDashboard(BaseModel):
    month: int
    pl: ExecutivePLSummary
    kpis: ExecutiveKPISummary
    operations: ExecutiveOpsSummary
    issues: ExecutiveIssueSummary
    improvements: ExecutiveImprovementSummary
    portfolio_summary: Optional[ExecutivePortfolioSummary] = None
    meeting: Optional[ExecutiveMeetingSummary] = None
    meeting_timeline: Optional[List[ExecutiveMeetingTimelineItem]] = None
    mid_term_plan_summary: Optional[MidTermPlanSummary] = None
    ceo_persona: Optional[CeoPersonaSummary] = None
    narrative_summary: Optional[ExecutiveNarrativeSummary] = None
    latest_narrative_period: Optional[str] = None
    latest_narrative_summary: Optional[str] = None
    latest_report_period: Optional[str] = None
    latest_report_title: Optional[str] = None
    latest_report_summary: Optional[str] = None
    reports: List[ReportSummary] = Field(default_factory=list)
    quarterly_review: Optional[QuarterlyReviewSummary] = None
    ceo_succession: Optional[CeoSuccessionSummary] = None
    culture: Optional[CultureSummary] = None
    environment: Optional[ExternalEnvironmentSummary] = None
    customer_summary: Optional[ExecutiveCustomerSummary] = None
    organization_summary: Optional[ExecutiveOrganizationSummary] = None
    financial_summary: Optional[ExecutiveFinancialSummary] = None
    execution_summary: Optional[ExecutiveExecutionSummary] = None
    forecast: Optional[Dict[str, object]] = None
    corporate_memory_summary: Optional[CorporateMemorySummary] = None
    strategy_v2_summary: Optional[StrategyV2Summary] = None
    multi_company_comparison_summary: Optional[MultiCompanyComparisonSummary] = None
    executive_simulation_summary: Optional[ExecutiveSimulationSummary] = None
    enterprise_autopilot_summary: Optional[AutopilotSummary] = None
