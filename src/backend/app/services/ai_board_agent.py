from typing import Dict, List, Optional

from .ai_ceo_agent import AICeoPersona
from ..models.executive_meeting_model import BoardDecision, DecisionOption
from ..models.board_member_model import BoardMemberOpinion
from ..models.ceo_succession_model import CeoCandidate, CeoSuccessionDecision
from ..models.external_environment_model_v2 import ExternalEnvironmentState
from .ai_board_members import BaseBoardMember, FinancialDirector, BrandDirector, RiskDirector, OrgDirector


class AIBoardAgent:
    def __init__(self, members: Optional[List[BaseBoardMember]] = None):
        self.members = members or [
            FinancialDirector(),
            BrandDirector(),
            RiskDirector(),
            OrgDirector(),
        ]
    def review_ceo_decision(
        self,
        ceo_option: DecisionOption,
        ceo_rationale: str,
        options: List[DecisionOption],
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        ceo_persona: AICeoPersona,
        environment: Optional[ExternalEnvironmentState | Dict[str, object]] = None,
    ) -> BoardDecision:
        if isinstance(environment, dict):
            try:
                environment = ExternalEnvironmentState(**environment)
            except Exception:
                environment = None
        opinions = []
        for member in self.members:
            op = member.evaluate(
                ceo_option=ceo_option,
                options=options,
                financials=financials,
                market_state=market_state,
                org_state=org_state,
                ceo_persona=ceo_persona,
                environment=environment,
            )
            opinions.append(op)

        # 集約ロジック
        risk_flags = sum(1 for op in opinions if op.risk_flag)
        preferred_options = [op.preferred_option_id for op in opinions]
        ceo_support = sum(1 for op in preferred_options if op == ceo_option.id)

        if risk_flags >= 2:
            status = "rejected"
            final_option_id = max(set(preferred_options), key=preferred_options.count)  # 多数決
            final_option = next((opt for opt in options if opt.id == final_option_id), ceo_option)
            board_rationale = f"複数の取締役からリスク指摘あり。代替案を採用。"
            conditions = "リスク軽減策の実施を条件に再検討"
        elif ceo_support >= len(opinions) * 0.75:
            status = "approved"
            final_option_id = ceo_option.id
            final_option = ceo_option
            board_rationale = f"取締役会としてCEO案を支持。"
            conditions = None
        else:
            status = "conditional"
            final_option_id = max(set(preferred_options), key=preferred_options.count)
            final_option = next((opt for opt in options if opt.id == final_option_id), ceo_option)
            board_rationale = f"CEO案に一部異論あり。修正案を採用。"
            conditions = "CEOとの協議を経て最終決定"

        return BoardDecision(
            status=status,
            final_option_id=final_option_id,
            final_option_label=final_option.label,
            board_rationale=board_rationale,
            conditions=conditions,
            member_opinions=opinions,
        )

    def select_next_ceo(
        self,
        candidates: List[CeoCandidate],
        board_members: Optional[List[BaseBoardMember]] = None,
        current_financials: Optional[Dict[str, object]] = None,
        market_state: Optional[Dict[str, object]] = None,
        org_state: Optional[Dict[str, object]] = None,
    ) -> CeoSuccessionDecision:
        board_members = board_members or self.members
        current_financials = current_financials or {}
        market_state = market_state or {}
        org_state = org_state or {}

        votes: Dict[str, str] = {}
        score_card: Dict[str, int] = {}

        for member in board_members:
            selected = self._evaluate_candidate_for_member(
                member,
                candidates,
                current_financials,
                market_state,
                org_state,
            )
            votes[member.role] = selected.candidate_id
            score_card[selected.candidate_id] = score_card.get(selected.candidate_id, 0) + 1

        top_score = max(score_card.values()) if score_card else 0
        tied_candidates = [cid for cid, score in score_card.items() if score == top_score]
        selected_candidate_id = tied_candidates[0] if tied_candidates else candidates[0].candidate_id

        risk_director_vote = votes.get('risk')
        if len(tied_candidates) > 1 and risk_director_vote in tied_candidates:
            selected_candidate_id = risk_director_vote

        rationale = (
            f"取締役会投票により候補{selected_candidate_id}を選択。"
            f"得票: {','.join(f'{role}:{vote}' for role, vote in votes.items())}"
        )
        transition_notes = (
            'リスク評価を重視し、経営安定性を確保するための世代交代です。'
            if risk_director_vote == selected_candidate_id and len(tied_candidates) > 1
            else None
        )

        return CeoSuccessionDecision(
            selected_candidate_id=selected_candidate_id,
            rationale=rationale,
            board_votes=votes,
            transition_notes=transition_notes,
        )

    def _evaluate_candidate_for_member(
        self,
        member: BaseBoardMember,
        candidates: List[CeoCandidate],
        current_financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
    ) -> CeoCandidate:
        best_candidate = candidates[0]
        best_score = -1.0

        for candidate in candidates:
            persona = candidate.persona
            score = 0.0
            if member.role == 'financial':
                cash_balance = float(current_financials.get('cash_balance', 0.0))
                score = (1 - candidate.innovation_bias) * 0.6 + candidate.similarity_to_current * 0.4
                if cash_balance < 2.0:
                    score -= 0.2
            elif member.role == 'brand':
                score = persona.brand_priority * 0.6 + persona.long_term_focus * 0.4
            elif member.role == 'risk':
                score = (1.0 - persona.aggressiveness) * 0.5 + (1.0 - persona.risk_tolerance) * 0.5
            elif member.role == 'org':
                score = (1.0 - persona.short_term_focus) * 0.5 + (1.0 - persona.aggressiveness) * 0.5

            if score > best_score:
                best_score = score
                best_candidate = candidate

        return best_candidate

    def _find_more_conservative_option(self, options: List[DecisionOption], ceo_option: DecisionOption) -> DecisionOption:
        lower_risk = [opt for opt in options if opt.risk_level in {'Low', 'Medium'} and opt.id != ceo_option.id]
        if lower_risk:
            return sorted(lower_risk, key=lambda x: ({'Low': 0, 'Medium': 1}.get(x.risk_level, 2), -float(x.long_term_value or 0.0)))[0]
        return ceo_option

    def _calculate_workload(self, org_state: Dict[str, object]) -> float:
        units = org_state.get('units', [])
        if not isinstance(units, list) or not units:
            return 0.0
        workloads = [unit.get('workload_index', 0.0) for unit in units if isinstance(unit, dict)]
        return float(sum(workloads) / len(workloads)) if workloads else 0.0
