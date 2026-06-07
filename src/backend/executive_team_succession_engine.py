from typing import Dict, List

from executive_team_succession_model import (
    ExecutiveCandidate,
    ExecutivePersona,
    ExecutiveRole,
)


class ExecutiveTeamSuccessionEngine:
    def generate_executive_candidates(
        self,
        current_persona: ExecutivePersona,
        role: ExecutiveRole,
        history: List[Dict],  # Placeholder for ExecutivePerformanceSnapshot
        num_candidates: int = 3
    ) -> List[ExecutiveCandidate]:
        candidates = [
            self._build_candidate(
                candidate_id='A',
                description='継承型',
                base=current_persona,
                adjustments=self._get_inheritance_adjustments(role),
                innovation_bias=0.05,
            ),
            self._build_candidate(
                candidate_id='B',
                description='攻め型',
                base=current_persona,
                adjustments=self._get_aggressive_adjustments(role),
                innovation_bias=0.15,
            ),
            self._build_candidate(
                candidate_id='C',
                description='守り型',
                base=current_persona,
                adjustments=self._get_defensive_adjustments(role),
                innovation_bias=0.10,
            ),
        ]

        if num_candidates < len(candidates):
            return candidates[:num_candidates]
        return candidates

    def _get_inheritance_adjustments(self, role: ExecutiveRole) -> Dict[str, float]:
        # 現在の役員に近い調整
        return {'risk_tolerance': -0.05}

    def _get_aggressive_adjustments(self, role: ExecutiveRole) -> Dict[str, float]:
        adjustments = {'innovation_bias': 0.1}
        if role == ExecutiveRole.CFO:
            adjustments['financial_focus'] = 0.1
        elif role == ExecutiveRole.COO:
            adjustments['operational_focus'] = 0.1
        elif role == ExecutiveRole.CMO:
            adjustments['brand_focus'] = 0.1
        elif role == ExecutiveRole.CHRO:
            adjustments['people_focus'] = 0.1
        return adjustments

    def _get_defensive_adjustments(self, role: ExecutiveRole) -> Dict[str, float]:
        adjustments = {'risk_tolerance': -0.1}
        if role == ExecutiveRole.CFO:
            adjustments['financial_focus'] = 0.1
        elif role == ExecutiveRole.COO:
            adjustments['operational_focus'] = 0.1
        elif role == ExecutiveRole.CMO:
            adjustments['brand_focus'] = 0.1
        elif role == ExecutiveRole.CHRO:
            adjustments['people_focus'] = 0.1
        return adjustments

    def _build_candidate(
        self,
        candidate_id: str,
        description: str,
        base: ExecutivePersona,
        adjustments: Dict[str, float],
        innovation_bias: float,
    ) -> ExecutiveCandidate:
        persona_data = base.model_dump()
        for key, delta in adjustments.items():
            if key in persona_data:
                persona_data[key] = self._clamp(persona_data[key] + delta)

        candidate_persona = ExecutivePersona(**persona_data)
        similarity = self._calculate_similarity(base, candidate_persona)
        strengths = self._extract_strengths(candidate_persona, base, description)
        weaknesses = self._extract_weaknesses(candidate_persona, base, description)

        return ExecutiveCandidate(
            candidate_id=candidate_id,
            role=base.role,
            persona=candidate_persona,
            strengths=strengths,
            weaknesses=weaknesses,
            similarity_to_current=similarity,
            innovation_bias=innovation_bias,
        )

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    def _calculate_similarity(self, current: ExecutivePersona, candidate: ExecutivePersona) -> float:
        current_data = current.model_dump()
        candidate_data = candidate.model_dump()
        delta = sum(abs(current_data[key] - candidate_data[key]) for key in current_data if key != 'role')
        similarity = max(0.0, 1.0 - delta / (len(current_data) - 1))
        return round(similarity, 3)

    def _extract_strengths(self, candidate: ExecutivePersona, current: ExecutivePersona, description: str) -> List[str]:
        strengths = []
        if description == '継承型':
            strengths.append('現在のスタイルを継承し安定性が高い')
        elif description == '攻め型':
            strengths.append('革新性が高く成長を促進')
        elif description == '守り型':
            strengths.append('リスク管理が強く安定を重視')
        return strengths

    def _extract_weaknesses(self, candidate: ExecutivePersona, current: ExecutivePersona, description: str) -> List[str]:
        weaknesses = []
        if description == '継承型':
            weaknesses.append('変化への適応が遅れる可能性')
        elif description == '攻め型':
            weaknesses.append('リスクが高くなる可能性')
        elif description == '守り型':
            weaknesses.append('成長機会を逃す可能性')
        return weaknesses