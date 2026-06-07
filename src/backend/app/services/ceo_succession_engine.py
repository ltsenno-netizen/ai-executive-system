from typing import Dict, List

from ..models.ai_ceo_model import AICeoPersona
from ..models.ceo_learning_model import CeoLearningSnapshot
from ..models.ceo_succession_model import CeoCandidate


class CeoSuccessionEngine:
    def generate_ceo_candidates(
        self,
        current_persona: AICeoPersona,
        learning_history: List[CeoLearningSnapshot],
        num_candidates: int = 3,
    ) -> List[CeoCandidate]:
        candidates = [
            self._build_candidate(
                candidate_id='A',
                description='継承型',
                base=current_persona,
                adjustments={'risk_tolerance': -0.05},
                innovation_bias=0.05,
            ),
            self._build_candidate(
                candidate_id='B',
                description='攻め型',
                base=current_persona,
                adjustments={'aggressiveness': 0.1, 'brand_priority': 0.1},
                innovation_bias=0.25,
            ),
            self._build_candidate(
                candidate_id='C',
                description='守り型',
                base=current_persona,
                adjustments={'risk_tolerance': -0.1, 'short_term_focus': -0.1},
                innovation_bias=0.15,
            ),
        ]

        if num_candidates < len(candidates):
            return candidates[:num_candidates]
        return candidates

    def _build_candidate(
        self,
        candidate_id: str,
        description: str,
        base: AICeoPersona,
        adjustments: Dict[str, float],
        innovation_bias: float,
    ) -> CeoCandidate:
        persona_data = base.model_dump()
        for key, delta in adjustments.items():
            if key in persona_data:
                persona_data[key] = self._clamp(persona_data[key] + delta)

        candidate_persona = AICeoPersona(**persona_data)
        similarity = self._calculate_similarity(base, candidate_persona)
        strengths = self._extract_strengths(candidate_persona, base)
        weaknesses = self._extract_weaknesses(candidate_persona, base)

        return CeoCandidate(
            candidate_id=candidate_id,
            persona=candidate_persona,
            strengths=strengths,
            weaknesses=weaknesses,
            similarity_to_current=similarity,
            innovation_bias=innovation_bias,
        )

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    def _calculate_similarity(self, current: AICeoPersona, candidate: AICeoPersona) -> float:
        current_data = current.model_dump()
        candidate_data = candidate.model_dump()
        delta = sum(abs(current_data[key] - candidate_data[key]) for key in current_data)
        similarity = max(0.0, 1.0 - delta / len(current_data))
        return round(similarity, 3)

    def _extract_strengths(self, candidate: AICeoPersona, current: AICeoPersona) -> List[str]:
        strengths = []
        if candidate.aggressiveness >= current.aggressiveness:
            strengths.append('成長志向が強い')
        else:
            strengths.append('リスク管理に強い')

        if candidate.brand_priority >= current.brand_priority:
            strengths.append('ブランド価値の維持・向上に注力')
        else:
            strengths.append('短期業績を重視')

        if candidate.long_term_focus >= current.long_term_focus:
            strengths.append('長期視点での戦略構築が得意')
        else:
            strengths.append('短期実行のスピード感がある')

        return strengths

    def _extract_weaknesses(self, candidate: AICeoPersona, current: AICeoPersona) -> List[str]:
        weaknesses = []
        if candidate.risk_tolerance < current.risk_tolerance:
            weaknesses.append('慎重すぎて機会の取りこぼしがある')
        else:
            weaknesses.append('過度なリスクを取る傾向がある')

        if candidate.short_term_focus < current.short_term_focus:
            weaknesses.append('短期対応がやや弱くなる可能性')
        else:
            weaknesses.append('短期成果を優先しすぎる可能性')

        if candidate.brand_priority < current.brand_priority:
            weaknesses.append('ブランド継続性の維持に課題が出る可能性')
        return weaknesses
