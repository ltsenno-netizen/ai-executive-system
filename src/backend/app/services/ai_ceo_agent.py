from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from ..models.ai_ceo_model import AICeoPersona
from ..models.executive_meeting_model import DecisionOption
from ..models.culture_model import CultureProfile
from ..models.external_environment_model_v2 import ExternalEnvironmentState


HORIPRO_2026_PERSONA = AICeoPersona(
    aggressiveness=0.7,
    risk_tolerance=0.6,
    brand_priority=0.8,
    short_term_focus=0.6,
    long_term_focus=0.8,
)


def load_latest_persona() -> AICeoPersona:
    from .ceo_learning_service import CeoLearningService
    service = CeoLearningService()
    return service.get_latest_persona() or HORIPRO_2026_PERSONA


class AICeoAgent:
    def __init__(self, persona: Optional[AICeoPersona] = None, culture: Optional[CultureProfile] = None, environment: Optional[ExternalEnvironmentState] = None):
        self.persona = persona or load_latest_persona()
        self.culture = culture or self._load_latest_culture()
        self.environment = environment or self._load_latest_environment()

    def _load_latest_culture(self) -> Optional[CultureProfile]:
        from .culture_service import CultureService
        try:
            service = CultureService()
            return service.get_latest_culture()
        except Exception:
            return None

    def _load_latest_environment(self) -> Optional[ExternalEnvironmentState]:
        from .external_environment_service_v2 import ExternalEnvironmentServiceV2
        try:
            service = ExternalEnvironmentServiceV2()
            return service.get_latest_environment()
        except Exception:
            return None

    def get_persona(self) -> AICeoPersona:
        return self.persona

    def select_option(
        self,
        options: List[DecisionOption],
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        execution_state: Optional[Dict[str, object]] = None,
    ) -> Tuple[DecisionOption, str]:
        execution_state = execution_state or {}
        persona = self.persona
        cash_balance = float(financials.get('cash_balance', 0.0))
        market_index = market_state.get('market_index_by_segment', {})
        market_strength = float(sum(market_index.values()) / len(market_index)) if market_index else 1.0
        workload_index = self._calculate_workload(org_state)
        execution_capacity = float(execution_state.get('capacity', max(0.0, 1.2 - workload_index)))
        execution_efficiency = float(execution_state.get('efficiency', max(0.0, 1.0 - workload_index * 0.2)))

        best_option = None
        best_score = float('-inf')

        for option in options:
            score = self._score_option(
                option,
                self.persona,
                cash_balance,
                market_strength,
                workload_index,
                execution_capacity,
                execution_efficiency,
                self.culture,
                self.environment,
            )
            if score > best_score:
                best_score = score
                best_option = option

        rationale = self._build_rationale(
            best_option,
            self.persona,
            cash_balance,
            market_strength,
            workload_index,
            execution_capacity,
            execution_efficiency,
        )
        return best_option, rationale
    def _score_option(
        self,
        option: DecisionOption,
        persona: AICeoPersona,
        cash_balance: float,
        market_strength: float,
        workload_index: float,
        execution_capacity: float,
        execution_efficiency: float,
        culture: Optional[CultureProfile] = None,
        environment: Optional[ExternalEnvironmentState] = None,
    ) -> float:
        risk_penalty = self._risk_penalty(option)
        financial_safety = self._financial_safety_score(option, cash_balance)
        execution_feasibility = self._execution_feasibility_score(option, execution_capacity)
        market_opportunity = self._market_opportunity_score(option, market_strength)
        org_sustainability = self._org_sustainability_score(option, workload_index)

        growth_score = float(getattr(option, 'growth_score', None) or option.expected_impact_score or 0.0)
        brand_score = float(getattr(option, 'brand_impact', None) or 0.0)
        short_term_score = float(getattr(option, 'short_term_profit', None) or 0.0)
        long_term_score = float(getattr(option, 'long_term_value', None) or 0.0)

        adjusted_persona = AICeoPersona(**persona.model_dump())
        aggressiveness_factor = adjusted_persona.aggressiveness
        if cash_balance < 2.5:
            aggressiveness_factor *= 0.35
        elif cash_balance < 5.0:
            aggressiveness_factor *= 0.7

        # 文化が意思決定に影響を与える
        if culture:
            aggressiveness_factor += culture.aggressiveness_culture * 0.1
            brand_score_adjustment = culture.brand_culture * 0.15
            brand_score = (brand_score + brand_score_adjustment) / 2.0 if brand_score > 0 else brand_score_adjustment
            growth_score_adjustment = culture.innovation_culture * 0.08
            growth_score = (growth_score + growth_score_adjustment) / 2.0 if growth_score > 0 else growth_score_adjustment
            risk_penalty *= (1.0 - culture.stability_culture * 0.2)

        # 外部環境が意思決定に影響を与える
        if environment:
            if environment.pest.economic < 0.5:
                adjusted_persona.risk_tolerance = max(0.0, adjusted_persona.risk_tolerance - 0.05)
                market_opportunity = max(0.0, market_opportunity - 0.1)
            if environment.pest.technological > 0.7:
                growth_score += 0.2
                market_opportunity = min(1.0, market_opportunity + 0.1)
            competitor_agg = sum(c.aggressiveness for c in environment.competitors) / len(environment.competitors) if environment.competitors else 0
            adjusted_persona.aggressiveness = min(1.0, adjusted_persona.aggressiveness + competitor_agg * 0.1)
            aggressiveness_factor = adjusted_persona.aggressiveness

        score = (
            aggressiveness_factor * growth_score
            + adjusted_persona.brand_priority * brand_score
            + adjusted_persona.short_term_focus * short_term_score
            + adjusted_persona.long_term_focus * long_term_score
            + 0.25 * financial_safety
            + 0.18 * execution_feasibility
            + 0.2 * market_opportunity
            + 0.2 * org_sustainability
            - (1.0 - adjusted_persona.risk_tolerance) * risk_penalty
        )
        return score
    def _financial_safety_score(self, option: DecisionOption, cash_balance: float) -> float:
        if cash_balance < 2.5:
            return 1.0 if option.id == 'B' else 0.6 if option.id == 'C' else 0.3
        if cash_balance < 5.0:
            return 0.8 if option.id == 'B' else 0.7 if option.id == 'C' else 0.5
        return 0.7 if option.id == 'B' else 0.8 if option.id == 'C' else 0.9

    def _execution_feasibility_score(self, option: DecisionOption, execution_capacity: float) -> float:
        if execution_capacity < 0.6:
            return 0.9 if option.id == 'B' else 0.7 if option.id == 'C' else 0.3
        if execution_capacity < 0.8:
            return 0.8 if option.id == 'B' else 0.8 if option.id == 'C' else 0.5
        return 0.7 if option.id == 'B' else 0.8 if option.id == 'C' else 0.9

    def _market_opportunity_score(self, option: DecisionOption, market_strength: float) -> float:
        if market_strength > 1.2:
            return 0.9 if option.id == 'A' else 0.7 if option.id == 'C' else 0.4
        if market_strength > 0.9:
            return 0.7 if option.id == 'A' else 0.7 if option.id == 'C' else 0.6
        return 0.4 if option.id == 'A' else 0.7 if option.id == 'B' else 0.6

    def _org_sustainability_score(self, option: DecisionOption, workload_index: float) -> float:
        if workload_index > 1.0:
            return 0.9 if option.id == 'B' else 0.7 if option.id == 'C' else 0.4
        return 0.7 if option.id == 'B' else 0.8 if option.id == 'C' else 0.8

    def _risk_penalty(self, option: DecisionOption) -> float:
        if option.risk_level == 'High':
            return 0.9
        if option.risk_level == 'Medium':
            return 0.6
        if option.risk_level == 'Low':
            return 0.3
        return 0.5

    def _calculate_workload(self, org_state: Dict[str, object]) -> float:
        units = org_state.get('units', [])
        if not isinstance(units, list) or not units:
            return 0.0
        workloads = [unit.get('workload_index', 0.0) for unit in units if isinstance(unit, dict)]
        return float(sum(workloads) / len(workloads)) if workloads else 0.0

    def _build_rationale(
        self,
        option: DecisionOption,
        persona: AICeoPersona,
        cash_balance: float,
        market_strength: float,
        workload_index: float,
        execution_capacity: float,
        execution_efficiency: float,
    ) -> str:
        reasons = [
            'このCEOはホリプロ2026年の「攻め×回転率×ブランド戦略」を意識しています',
        ]

        if cash_balance < 2.5:
            reasons.append('現金余力が限定的なため、キャッシュ保全を優先しました')
        if market_strength > 1.2:
            reasons.append('市場機会が強く、成長投資を支援するタイミングです')
        if workload_index > 1.0:
            reasons.append('組織負荷を考慮し、実行可能な選択を重視しました')
        if execution_capacity < 0.7:
            reasons.append('実行力が限定的なため、過度な負荷は避けました')

        if persona.brand_priority >= 0.7:
            reasons.append('ブランド価値を損なわず、IPと興行の価値を守る判断を行いました')
        if persona.short_term_focus >= 0.5:
            reasons.append('ライブ・配信・TVの回転収益を確保する視点も持っています')
        if persona.long_term_focus >= 0.7:
            reasons.append('中期的なブランド戦略を見据えた意思決定です')

        if option.id == 'A':
            reasons.append('攻めの投資継続を選び、大型興行や舞台の成長機会を優先しました')
        elif option.id == 'B':
            reasons.append('守りの選択を選び、財務健全性と短期安定性を重視しました')
        else:
            reasons.append('バランス型を選択し、成長と安定性を両立する判断を行いました')

        return f"AI CEOは{option.label}を選択しました。理由: {'。'.join(reasons)}。"
