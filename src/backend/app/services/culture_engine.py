from typing import Dict, List, Optional

from ..models.ai_ceo_model import AICeoPersona
from ..models.culture_model import CultureProfile
from ..models.executive_meeting_model import BoardDecision
from ..models.external_environment_model_v2 import ExternalEnvironmentState
from ..models.quarterly_review_model import QuarterlyReview


class CultureEngine:
    """
    企業文化を CEO, Board, 四半期レビューから更新する
    """

    def update_culture(
        self,
        previous_culture: Optional[CultureProfile],
        ceo_persona: AICeoPersona,
        board_decisions: List[BoardDecision],
        quarterly_review: Optional[QuarterlyReview],
        environment: Optional[ExternalEnvironmentState] = None,
    ) -> Dict[str, float]:
        """
        文化を更新
        前月文化 → CEO 影響 → Board 影響 → 四半期レビュー影響 → 自然減衰
        """
        # 初期化: 前月文化か初期値
        if previous_culture:
            culture = previous_culture.model_dump()
            culture.pop('period', None)
            culture.pop('notes', None)
        else:
            culture = self._get_base_culture()

        # CEO パーソナから文化への影響
        culture = self._apply_ceo_influence(culture, ceo_persona)

        # Board 決定から文化への影響
        culture = self._apply_board_influence(culture, board_decisions)

        # 四半期レビューから文化への影響
        if quarterly_review:
            culture = self._apply_quarterly_influence(culture, quarterly_review)

        # 外部環境から文化への影響
        if environment:
            culture = self._apply_environment_influence(culture, environment)

        # 文化の自然減衰（徐々に変わる、急には変わらない）
        culture = self._apply_natural_decay(culture)

        return culture

    def _apply_environment_influence(self, culture: Dict[str, float], environment: ExternalEnvironmentState) -> Dict[str, float]:
        """
        外部環境が文化に与える影響
        recession → stability_culture +0.02
        technological → innovation_culture +0.03
        """
        if any(shock.shock_type == "recession" for shock in environment.shocks):
            culture['stability_culture'] = self._clamp(culture['stability_culture'] + 0.02)
        if environment.pest.technological > 0.7:
            culture['innovation_culture'] = self._clamp(culture['innovation_culture'] + 0.03)
        return culture

    def _get_base_culture(self) -> Dict[str, float]:
        """初期の企業文化"""
        return {
            'aggressiveness_culture': 0.5,
            'risk_aversion_culture': 0.5,
            'brand_culture': 0.5,
            'cost_culture': 0.5,
            'people_culture': 0.5,
            'execution_culture': 0.5,
            'innovation_culture': 0.5,
            'stability_culture': 0.5,
        }

    def _apply_ceo_influence(self, culture: Dict[str, float], ceo_persona: AICeoPersona) -> Dict[str, float]:
        """
        CEO のパーソナリティが文化に反映される
        CEO が攻め寄り → aggressiveness_culture UP
        """
        # CEO の攻撃性 → 攻め文化
        if ceo_persona.aggressiveness >= 0.7:
            culture['aggressiveness_culture'] = self._clamp(culture['aggressiveness_culture'] + 0.02)
        elif ceo_persona.aggressiveness <= 0.3:
            culture['aggressiveness_culture'] = self._clamp(culture['aggressiveness_culture'] - 0.02)

        # CEO のリスク許容度 → 守り文化（逆相関）
        if ceo_persona.risk_tolerance <= 0.3:
            culture['risk_aversion_culture'] = self._clamp(culture['risk_aversion_culture'] + 0.02)
        elif ceo_persona.risk_tolerance >= 0.7:
            culture['risk_aversion_culture'] = self._clamp(culture['risk_aversion_culture'] - 0.02)

        # CEO のブランド優先度
        if ceo_persona.brand_priority >= 0.7:
            culture['brand_culture'] = self._clamp(culture['brand_culture'] + 0.02)

        # CEO の短期志向 → コスト重視
        if ceo_persona.short_term_focus >= 0.7:
            culture['cost_culture'] = self._clamp(culture['cost_culture'] + 0.01)

        # CEO の長期志向 → イノベーション
        if ceo_persona.long_term_focus >= 0.75:
            culture['innovation_culture'] = self._clamp(culture['innovation_culture'] + 0.01)

        return culture

    def _apply_board_influence(self, culture: Dict[str, float], board_decisions: List[BoardDecision]) -> Dict[str, float]:
        """
        Board の判断傾向が文化に反映される
        RiskDirector が反対しがち → 守り文化 UP
        """
        if not board_decisions:
            return culture

        rejected_count = sum(1 for d in board_decisions if d.status == "rejected")
        approved_count = sum(1 for d in board_decisions if d.status == "approved")

        # 拒否が多い → 守り文化
        if rejected_count >= len(board_decisions) * 0.5:
            culture['risk_aversion_culture'] = self._clamp(culture['risk_aversion_culture'] + 0.01)

        # 承認が多い → 攻め文化
        if approved_count >= len(board_decisions) * 0.7:
            culture['aggressiveness_culture'] = self._clamp(culture['aggressiveness_culture'] + 0.01)

        return culture

    def _apply_quarterly_influence(self, culture: Dict[str, float], quarterly_review: QuarterlyReview) -> Dict[str, float]:
        """
        四半期レビューから文化への影響
        実行が良好 → 実行力文化 UP
        イノベーション成功 → イノベーション文化 UP
        """
        # 実行負荷が高い場合
        if hasattr(quarterly_review, 'execution') and quarterly_review.execution:
            org_load = getattr(quarterly_review.execution, 'org_load_index', 0.0)
            if org_load > 0.8:
                culture['execution_culture'] = self._clamp(culture['execution_culture'] + 0.02)

        # 財務成績が良い場合
        if hasattr(quarterly_review, 'financial') and quarterly_review.financial:
            revenue_vs_plan = getattr(quarterly_review.financial, 'revenue_vs_plan', 0.0)
            if revenue_vs_plan > 0.1:
                culture['innovation_culture'] = self._clamp(culture['innovation_culture'] + 0.02)

        # Board 承認が高い場合
        if hasattr(quarterly_review, 'board_review') and quarterly_review.board_review:
            status = getattr(quarterly_review.board_review, 'status', 'no_review')
            if status == 'approved':
                culture['stability_culture'] = self._clamp(culture['stability_culture'] + 0.01)

        return culture

    def _apply_natural_decay(self, culture: Dict[str, float]) -> Dict[str, float]:
        """
        文化は徐々に変わる（急激には変わらない）
        前月文化が強すぎると 0.99 倍で減衰
        """
        decay_factor = 0.99
        for key in culture:
            # 0.5 に向けて緩やかに収束
            mid = 0.5
            delta = culture[key] - mid
            culture[key] = mid + delta * decay_factor
            culture[key] = self._clamp(culture[key])

        return culture

    def _clamp(self, value: float) -> float:
        """値を 0.0-1.0 に制限"""
        return max(0.0, min(1.0, value))
