from typing import Dict, List, Optional
from ..models.executive_meeting_model import DecisionOption
from ..models.ai_ceo_model import AICeoPersona
from ..models.culture_model import CultureProfile
from ..models.external_environment_model_v2 import ExternalEnvironmentState


class BaseBoardMember:
    role: str

    def evaluate(
        self,
        ceo_option: DecisionOption,
        options: List[DecisionOption],
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        ceo_persona: AICeoPersona,
        culture: Optional[CultureProfile] = None,
        environment: Optional[ExternalEnvironmentState] = None,
    ) -> 'BoardMemberOpinion':
        raise NotImplementedError


class FinancialDirector(BaseBoardMember):
    role = "financial"

    def evaluate(
        self,
        ceo_option: DecisionOption,
        options: List[DecisionOption],
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        ceo_persona: AICeoPersona,
        culture: Optional[CultureProfile] = None,
        environment: Optional[ExternalEnvironmentState] = None,
    ) -> 'BoardMemberOpinion':
        from ..models.board_member_model import BoardMemberOpinion

        cash_balance = float(financials.get('cash_balance', 0.0))
        operating_profit = float(financials.get('operating_profit', 0.0))
        capex_impact = float(ceo_option.short_term_profit or 0.0) * -1  # Negative impact on cash

        # 文化が強いと保守的になる
        cash_threshold = 2.0
        if culture and culture.cost_culture > 0.7:
            cash_threshold = 2.5  # より厳しい閾値

        # 財務寄り: キャッシュ・利益を重視
        if cash_balance + capex_impact < cash_threshold:  # Low cash threshold
            risk_flag = True
            preferred_option_id = options[0].id if options else ceo_option.id  # Conservative option
            rationale = f"キャッシュ残高が不足するリスクあり。投資を抑制すべき。"
        elif operating_profit < 0:
            risk_flag = True
            preferred_option_id = ceo_option.id
            rationale = f"利益がマイナス。財務健全性を優先。"
        else:
            risk_flag = False
            preferred_option_id = ceo_option.id
            rationale = f"財務指標が良好。投資を承認可能。"

        return BoardMemberOpinion(
            member_role=self.role,
            preferred_option_id=preferred_option_id,
            rationale=rationale,
            risk_flag=risk_flag,
        )


class BrandDirector(BaseBoardMember):
    role = "brand"

    def evaluate(
        self,
        ceo_option: DecisionOption,
        options: List[DecisionOption],
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        ceo_persona: AICeoPersona,
        culture: Optional[CultureProfile] = None,
        environment: Optional[ExternalEnvironmentState] = None,
    ) -> 'BoardMemberOpinion':
        from ..models.board_member_model import BoardMemberOpinion

        # ブランド寄り: 長期価値を重視
        # 文化がブランド重視だと、より積極的に支持
        brand_impact = float(getattr(ceo_option, 'brand_impact', 0.0) or 0.0)
        brand_threshold = 0.5
        if culture and culture.brand_culture > 0.7:
            brand_threshold = 0.3  # より低い閾値で支持

        # 外部環境: 競合の攻撃性が高いと、攻め案を支持
        competitor_agg = sum(c.aggressiveness for c in environment.competitors) / len(environment.competitors) if environment and environment.competitors else 0
        if competitor_agg > 0.5:
            brand_threshold -= 0.2

        if brand_impact > brand_threshold:  # 閾値
            risk_flag = False
            preferred_option_id = ceo_option.id
            rationale = f"ブランド価値向上の機会。長期視点で支持。"
        else:
            risk_flag = True
            preferred_option_id = options[0].id if options else ceo_option.id
            rationale = f"ブランド価値への寄与が薄い。慎重に検討すべき。"

        return BoardMemberOpinion(
            member_role=self.role,
            preferred_option_id=preferred_option_id,
            rationale=rationale,
            risk_flag=risk_flag,
        )


class RiskDirector(BaseBoardMember):
    role = "risk"

    def evaluate(
        self,
        ceo_option: DecisionOption,
        options: List[DecisionOption],
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        ceo_persona: AICeoPersona,
        culture: Optional[CultureProfile] = None,
        environment: Optional[ExternalEnvironmentState] = None,
    ) -> 'BoardMemberOpinion':
        from ..models.board_member_model import BoardMemberOpinion

        # リスク寄り: ダウンサイドを重視
        # 文化が安定性重視だと、より保守的になる
        risk_level_str = getattr(ceo_option, 'risk_level', 'Medium')
        risk_level = {'Low': 0.3, 'Medium': 0.5, 'High': 0.8}.get(risk_level_str, 0.5)
        market_volatility = market_state.get('volatility', 0.2)

        # 文化で調整
        risk_threshold = 0.7
        if culture and culture.stability_culture > 0.7:
            risk_threshold = 0.6  # より厳しく

        # 外部環境: 不況時はより厳しく
        if environment and any(shock.shock_type == "recession" for shock in environment.shocks):
            risk_threshold -= 0.1

        if risk_level > risk_threshold or market_volatility > 0.3:
            risk_flag = True
            preferred_option_id = options[0].id if options else ceo_option.id
            rationale = f"リスクが高すぎる。より安全な選択肢を検討。"
        else:
            risk_flag = False
            preferred_option_id = ceo_option.id
            rationale = f"リスクは許容範囲内。"

        return BoardMemberOpinion(
            member_role=self.role,
            preferred_option_id=preferred_option_id,
            rationale=rationale,
            risk_flag=risk_flag,
        )


class OrgDirector(BaseBoardMember):
    role = "org"

    def evaluate(
        self,
        ceo_option: DecisionOption,
        options: List[DecisionOption],
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        ceo_persona: AICeoPersona,
        culture: Optional[CultureProfile] = None,
        environment: Optional[ExternalEnvironmentState] = None,
    ) -> 'BoardMemberOpinion':
        from ..models.board_member_model import BoardMemberOpinion

        # 組織寄り: 実行負荷を重視
        # 文化が実行力重視だと、より高い負荷を受け入れる
        units = org_state.get('units', [])
        avg_workload = sum(unit.get('workload_index', 0.0) for unit in units if isinstance(unit, dict)) / len(units) if units else 0.0
        capacity = 1.0  # Assume capacity is 1.0

        # 文化で調整
        if culture and culture.execution_culture > 0.75:
            capacity = 1.2  # 実行力が高い文化なら、高い負荷も受け入れる

        if avg_workload > capacity:
            risk_flag = True
            preferred_option_id = options[0].id if options else ceo_option.id
            rationale = f"組織の実行キャパシティを超える。負荷を軽減すべき。"
        else:
            risk_flag = False
            preferred_option_id = ceo_option.id
            rationale = f"実行負荷は許容範囲内。"

        return BoardMemberOpinion(
            member_role=self.role,
            preferred_option_id=preferred_option_id,
            rationale=rationale,
            risk_flag=risk_flag,
        )