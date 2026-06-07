import json
import os
from typing import Dict, List, Optional

from ..models.ai_ceo_model import AICeoPersona
from ..models.ceo_succession_model import CeoCandidate, CeoSuccessionDecision
from .ceo_succession_engine import CeoSuccessionEngine
from .ai_board_agent import AIBoardAgent
from .ai_board_members import BaseBoardMember, FinancialDirector, BrandDirector, RiskDirector, OrgDirector
from .ceo_learning_service import CeoLearningService


class CeoSuccessionService:
    def __init__(self, succession_root: Optional[str] = None, persona_root: Optional[str] = None):
        self.engine = CeoSuccessionEngine()
        self.board_agent = AIBoardAgent()
        self.board_members: List[BaseBoardMember] = [
            FinancialDirector(),
            BrandDirector(),
            RiskDirector(),
            OrgDirector(),
        ]
        self.succession_root = succession_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/ceo_succession')
        )
        self.persona_root = persona_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../personas/ceo')
        )
        if os.path.abspath(self.succession_root) == os.path.abspath(self.persona_root):
            self.persona_root = os.path.join(self.succession_root, 'ceo_personas')
        self.ceo_learning_service = CeoLearningService(persona_root=self.persona_root)

        os.makedirs(self.succession_root, exist_ok=True)
        os.makedirs(self.persona_root, exist_ok=True)

    def run_ceo_succession(
        self,
        period: str,
        current_financials: Optional[Dict[str, object]] = None,
        market_state: Optional[Dict[str, object]] = None,
        org_state: Optional[Dict[str, object]] = None,
    ) -> CeoSuccessionDecision:
        current_persona = self.ceo_learning_service.get_latest_persona() or self.ceo_learning_service._get_base_persona()
        history = self.ceo_learning_service.build_learning_history(
            [self.ceo_learning_service._previous_period(period, i) for i in range(6, 0, -1)]
        )

        candidates = self.engine.generate_ceo_candidates(current_persona, history)
        decision = self.board_agent.select_next_ceo(
            candidates=candidates,
            board_members=self.board_members,
            current_financials=current_financials or {},
            market_state=market_state or {},
            org_state=org_state or {},
        )
        decision = CeoSuccessionDecision(
            period=period,
            selected_candidate_id=decision.selected_candidate_id,
            rationale=decision.rationale,
            board_votes=decision.board_votes,
            transition_notes=decision.transition_notes,
        )

        selected = next((candidate for candidate in candidates if candidate.candidate_id == decision.selected_candidate_id), None)
        if selected is None:
            raise ValueError('選ばれた後継者候補が存在しません。')

        self._save_succession_decision(period, decision)
        self.ceo_learning_service._save_persona(selected.persona, period)
        return decision

    def get_latest_succession_decision(self) -> Optional[CeoSuccessionDecision]:
        files = [f for f in os.listdir(self.succession_root) if f.endswith('.json')]
        if not files:
            return None
        files.sort()
        latest_file = files[-1]
        return self._load_succession_decision(latest_file)

    def _save_succession_decision(self, period: str, decision: CeoSuccessionDecision) -> None:
        path = os.path.join(self.succession_root, f'{period}.json')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(decision.model_dump_json(indent=2, ensure_ascii=False))

    def _load_succession_decision(self, filename: str) -> CeoSuccessionDecision:
        path = os.path.join(self.succession_root, filename)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return CeoSuccessionDecision(**data)

    def load_succession_history(self) -> List[CeoSuccessionDecision]:
        files = [f for f in os.listdir(self.succession_root) if f.endswith('.json')]
        history = [self._load_succession_decision(filename) for filename in sorted(files)]
        return history
