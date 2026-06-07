from typing import List
from ..models.ceo_learning_model import CeoLearningSnapshot
from ..models.ai_ceo_model import AICeoPersona


class CeoLearningEngine:
    def update_persona_from_history(
        self,
        base_persona: AICeoPersona,
        history: List[CeoLearningSnapshot],
    ) -> AICeoPersona:
        """
        ルール例：
        - 連続して利益未達 → aggressiveness を少し下げる
        - Board による rejected が多い → risk_tolerance を下げる
        - ブランド関連施策の成功が多い → brand_priority を上げる
        - 短期利益は出ているが中期計画未達 → short_term_focus を下げ、long_term_focus を上げる
        """
        if not history:
            return base_persona

        # 初期値コピー
        new_persona = base_persona.model_copy()

        # 連続利益未達のカウント
        consecutive_profit_shortfall = 0
        for snapshot in reversed(history[-12:]):  # 直近12ヶ月
            if snapshot.financial_result.operating_profit < 0:
                consecutive_profit_shortfall += 1
            else:
                break

        if consecutive_profit_shortfall >= 3:
            new_persona.aggressiveness = max(0.1, new_persona.aggressiveness - 0.1)

        # Board rejected の割合
        rejected_count = sum(1 for s in history if s.board_status == 'rejected')
        rejected_ratio = rejected_count / len(history) if history else 0
        if rejected_ratio > 0.3:
            new_persona.risk_tolerance = max(0.1, new_persona.risk_tolerance - 0.1)

        # ブランド成功の仮定（利益成長で代用）
        profit_growth_count = sum(1 for i in range(1, len(history)) if history[i].financial_result.operating_profit > history[i-1].financial_result.operating_profit)
        growth_ratio = profit_growth_count / max(1, len(history) - 1) if len(history) > 1 else 0
        if growth_ratio > 0.5:
            new_persona.brand_priority = min(1.0, new_persona.brand_priority + 0.05)

        # 短期 vs 長期のバランス（簡易）
        if consecutive_profit_shortfall >= 2 and rejected_ratio > 0.2:
            new_persona.short_term_focus = max(0.1, new_persona.short_term_focus - 0.05)
            new_persona.long_term_focus = min(1.0, new_persona.long_term_focus + 0.05)

        return new_persona