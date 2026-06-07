from typing import Dict, List, Optional, Tuple

from ..models.executive_meeting_model import (
    BoardDecision,
    DecisionOption,
    ExecutiveAgent,
    ExecutiveDebateSummary,
    MeetingAgendaItem,
    MeetingMinutes,
)
from .ai_board_agent import AIBoardAgent
from .ai_ceo_agent import AICeoAgent, AICeoPersona
from ..models.external_environment_model_v2 import ExternalEnvironmentState
from .ai_executive_agents import EXECUTIVE_ROLES, build_executive_agent


class ExecutiveMeetingEngine:
    def generate_executive_agents(self, agenda: List[MeetingAgendaItem]) -> List[ExecutiveAgent]:
        agenda_dicts = [item.model_dump() for item in agenda]
        agents = []
        for role in EXECUTIVE_ROLES:
            agent_data = build_executive_agent(role, agenda_dicts)
            agents.append(ExecutiveAgent(**agent_data))
        return agents

    def run_strategic_debate(self, agenda: List[MeetingAgendaItem], agents: List[ExecutiveAgent]) -> ExecutiveDebateSummary:
        opening_statements = agents
        cross_discussion = []
        consensus_points = []
        divergences = []

        if any(item.category == 'PL' for item in agenda):
            cross_discussion.append('Fuel growth while maintaining cash discipline is the central financial debate.')
            consensus_points.append('Protect liquidity while pursuing high-return investments.')
        if any(item.category == 'Portfolio' for item in agenda):
            cross_discussion.append('Portfolio actions should be sequenced with execution capacity and market timing.')
            divergences.append('Whether to accelerate investments now or preserve optionality for later.')
        if any(item.category == 'Operations' for item in agenda):
            cross_discussion.append('Operational cadence must be aligned with reported issue resolution timelines.')
            consensus_points.append('Operational stability is required before adding new major initiatives.')
        if any(item.category == 'Issues' for item in agenda):
            cross_discussion.append('Issue remediation must not overload teams during a high-risk market phase.')
            divergences.append('Debate between rapid action and conservative allocation persists.')

        consensus = ' and '.join(consensus_points) if consensus_points else 'The team agrees on cautious, coordinated execution.'
        if not divergences:
            divergences = ['Minor tactical preferences remain among the agents.']

        return ExecutiveDebateSummary(
            opening_statements=opening_statements,
            cross_discussion=cross_discussion,
            consensus=consensus,
            divergence=divergences,
        )

    def generate_decision_options(self, agenda: List[MeetingAgendaItem]) -> List[DecisionOption]:
        has_portfolio = any(item.category == 'Portfolio' for item in agenda)
        has_ops = any(item.category == 'Operations' for item in agenda)
        has_issues = any(item.category == 'Issues' for item in agenda)

        options = [
            DecisionOption(
                id='A',
                label='攻めの投資継続',
                actions=['execute_tranche_2', 'increase_marketing_10pct'] if has_portfolio else ['increase_marketing_10pct'],
                pros=['市場回復時の成長最大化', '高い戦略的機動性を維持'],
                cons=['キャッシュ逼迫リスク', '実行力に対する負荷増大'],
                risk_level='High',
                expected_impact_score=0.9,
                growth_score=0.9,
                brand_impact=0.8,
                short_term_profit=0.6,
                long_term_value=0.9,
            ),
            DecisionOption(
                id='B',
                label='守りの投資抑制',
                actions=['delay_tranche_2', 'freeze_hiring'] if has_portfolio else ['freeze_hiring'],
                pros=['流動性確保', 'オペレーションリスクの低減'],
                cons=['成長機会の遅延', '市場シェア回復の鈍化'],
                risk_level='Low',
                expected_impact_score=0.4,
                growth_score=0.4,
                brand_impact=0.3,
                short_term_profit=0.5,
                long_term_value=0.5,
            ),
            DecisionOption(
                id='C',
                label='バランス型',
                actions=['partial_tranche', 'reduce_production_cost'],
                pros=['リスク低減と成長維持', '組織負荷をコントロール'],
                cons=['意思決定が複雑', '実行には高い調整力が必要'],
                risk_level='Medium',
                expected_impact_score=0.65,
                growth_score=0.7,
                brand_impact=0.6,
                short_term_profit=0.55,
                long_term_value=0.75,
            ),
        ]
        return options

    def select_ceo_option(
        self,
        options: List[DecisionOption],
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        execution_state: Optional[Dict[str, object]] = None,
        environment: Optional[ExternalEnvironmentState] = None,
    ) -> Tuple[DecisionOption, str, AICeoPersona]:
        ceo = AICeoAgent(environment=environment)
        selected_option, rationale = ceo.select_option(options, financials, market_state, org_state, execution_state)
        return selected_option, rationale, ceo.get_persona()

    def review_board_decision(
        self,
        ceo_option: DecisionOption,
        ceo_rationale: str,
        options: List[DecisionOption],
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        ceo_persona: AICeoPersona,
        environment: Optional[ExternalEnvironmentState] = None,
    ) -> BoardDecision:
        board = AIBoardAgent()
        return board.review_ceo_decision(
            ceo_option=ceo_option,
            ceo_rationale=ceo_rationale,
            options=options,
            financials=financials,
            market_state=market_state,
            org_state=org_state,
            ceo_persona=ceo_persona,
            environment=environment,
        )

    def compile_meeting_minutes(
        self,
        month: int,
        agenda: List[MeetingAgendaItem],
        debate_summary: ExecutiveDebateSummary,
        decisions: List[Dict[str, object]],
        selected_option_id: str | None = None,
        ceo_comment: str | None = None,
    ) -> MeetingMinutes:
        summary = f"Month {month} executive meeting completed with {len(agenda)} agenda items."
        highlights = []

        highlights.append(f"Consensus: {debate_summary.consensus}")
        highlights.extend(debate_summary.cross_discussion[:2])
        if selected_option_id:
            highlights.append(f"CEO chose option {selected_option_id}.")
        if ceo_comment:
            highlights.append(f"CEO comment: {ceo_comment}")

        decisions_recorded = [
            {
                'agenda_id': decision.get('agenda_id'),
                'decision': decision.get('decision'),
                'comment': decision.get('comment'),
            }
            for decision in decisions
        ]

        return MeetingMinutes(
            summary=summary,
            discussion_highlights=highlights,
            decisions_recorded=decisions_recorded,
            ceo_comment=ceo_comment or '',
        )
