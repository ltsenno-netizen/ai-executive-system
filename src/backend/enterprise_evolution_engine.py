from typing import Dict, List, Optional
from pydantic import BaseModel

from app.models.culture_model import CultureProfile
from app.models.external_environment_model_v2 import ExternalEnvironmentState
from executive_team_succession_model import ExecutivePersona, ExecutiveRole
from app.models.executive_meeting_model import BoardDecision


class EnterpriseEvolutionResult(BaseModel):
    period: str
    culture_shift: Dict[str, float]
    leadership_shift: Dict[str, float]
    environment_pressure: float
    evolution_score: float
    notes: Optional[str] = None


class EnterpriseEvolutionEngine:
    def compute_enterprise_evolution(
        self,
        culture: CultureProfile,
        environment: ExternalEnvironmentState,
        executive_team: Dict[ExecutiveRole, ExecutivePersona],
        board_decisions: List[BoardDecision]
    ) -> EnterpriseEvolutionResult:
        # 3.1 外部環境 → 文化への影響
        culture_shift_env = self._compute_environment_to_culture_shift(environment)

        # 3.2 文化 → 経営チームへの影響
        leadership_shift_culture = self._compute_culture_to_leadership_shift(culture, executive_team)

        # 3.3 経営チーム → 文化への逆影響
        culture_shift_team = self._compute_leadership_to_culture_shift(executive_team)

        # 3.4 Board → 文化への影響
        culture_shift_board = self._compute_board_to_culture_shift(board_decisions)

        # 統合文化シフト
        total_culture_shift = self._merge_shifts([
            culture_shift_env,
            culture_shift_team,
            culture_shift_board
        ])

        # 3.5 進化スコア
        environment_pressure = self._compute_environment_pressure(environment)
        evolution_score = self._compute_evolution_score(
            total_culture_shift, leadership_shift_culture, environment_pressure
        )

        notes = self._generate_notes(total_culture_shift, leadership_shift_culture, environment_pressure)

        return EnterpriseEvolutionResult(
            period="",  # To be set by caller
            culture_shift=total_culture_shift,
            leadership_shift=leadership_shift_culture,
            environment_pressure=environment_pressure,
            evolution_score=evolution_score,
            notes=notes
        )

    def _compute_environment_to_culture_shift(self, environment: ExternalEnvironmentState) -> Dict[str, float]:
        shift = {}
        # 不況 → stability_culture +0.02
        if environment.pest.economic < 0.3:
            shift['stability_culture'] = shift.get('stability_culture', 0) + 0.02

        # 技術革新 → innovation_culture +0.03
        if environment.market_growth_modifier > 0.1:
            shift['innovation_culture'] = shift.get('innovation_culture', 0) + 0.03

        # 競合 aggressiveness → aggressiveness_culture +0.02
        avg_competitor_aggressiveness = sum(c.aggressiveness for c in environment.competitors) / len(environment.competitors) if environment.competitors else 0
        if avg_competitor_aggressiveness > 0.7:
            shift['aggressiveness_culture'] = shift.get('aggressiveness_culture', 0) + 0.02

        return shift

    def _compute_culture_to_leadership_shift(self, culture: CultureProfile, executive_team: Dict[ExecutiveRole, ExecutivePersona]) -> Dict[str, float]:
        shift = {}
        # brand_culture が高い → CMO の brand_focus +0.05
        if culture.brand_culture > 0.7 and ExecutiveRole.CMO in executive_team:
            shift['cmo_brand_focus'] = 0.05

        # people_culture が高い → CHRO の people_focus +0.05
        if culture.people_culture > 0.7 and ExecutiveRole.CHRO in executive_team:
            shift['chro_people_focus'] = 0.05

        # cost_culture が高い → CFO の financial_focus +0.05
        if culture.cost_culture > 0.7 and ExecutiveRole.CFO in executive_team:
            shift['cfo_financial_focus'] = 0.05

        return shift

    def _compute_leadership_to_culture_shift(self, executive_team: Dict[ExecutiveRole, ExecutivePersona]) -> Dict[str, float]:
        shift = {}
        # CFO が保守的 → risk_aversion_culture +0.02
        if ExecutiveRole.CFO in executive_team and executive_team[ExecutiveRole.CFO].risk_tolerance < 0.3:
            shift['risk_aversion_culture'] = shift.get('risk_aversion_culture', 0) + 0.02

        # COO が execution-heavy → execution_culture +0.03
        if ExecutiveRole.COO in executive_team and executive_team[ExecutiveRole.COO].operational_focus > 0.8:
            shift['execution_culture'] = shift.get('execution_culture', 0) + 0.03

        # CMO が攻め型 → aggressiveness_culture +0.02
        if ExecutiveRole.CMO in executive_team and executive_team[ExecutiveRole.CMO].innovation_bias > 0.7:
            shift['aggressiveness_culture'] = shift.get('aggressiveness_culture', 0) + 0.02

        return shift

    def _compute_board_to_culture_shift(self, board_decisions: List[BoardDecision]) -> Dict[str, float]:
        shift = {}
        # RiskDirector が反対しがち → stability_culture +0.01
        risk_oppositions = sum(1 for d in board_decisions if d.status in ['rejected', 'conditional'] and 'risk' in d.board_rationale.lower())
        if risk_oppositions > len(board_decisions) * 0.5:
            shift['stability_culture'] = shift.get('stability_culture', 0) + 0.01

        # BrandDirector が攻め案を支持 → brand_culture +0.02
        brand_supports = sum(1 for d in board_decisions if d.status == 'approved' and 'brand' in d.board_rationale.lower())
        if brand_supports > len(board_decisions) * 0.3:
            shift['brand_culture'] = shift.get('brand_culture', 0) + 0.02

        return shift

    def _merge_shifts(self, shifts: List[Dict[str, float]]) -> Dict[str, float]:
        merged = {}
        for shift in shifts:
            for key, value in shift.items():
                merged[key] = merged.get(key, 0) + value
        return merged

    def _compute_environment_pressure(self, environment: ExternalEnvironmentState) -> float:
        # 外部環境の圧力: 経済 + 競合 + ショック
        economic_pressure = abs(environment.pest.economic - 0.5)  # 0.5が中立
        competitor_pressure = sum(c.aggressiveness for c in environment.competitors) / len(environment.competitors) if environment.competitors else 0
        shock_pressure = len(environment.shocks) * 0.1
        return (economic_pressure + competitor_pressure + shock_pressure) / 3

    def _compute_evolution_score(self, culture_shift: Dict[str, float], leadership_shift: Dict[str, float], environment_pressure: float) -> float:
        culture_shift_total = sum(abs(v) for v in culture_shift.values())
        leadership_shift_total = sum(abs(v) for v in leadership_shift.values())
        return (
            culture_shift_total * 0.4 +
            leadership_shift_total * 0.3 +
            environment_pressure * 0.3
        )

    def _generate_notes(self, culture_shift: Dict[str, float], leadership_shift: Dict[str, float], environment_pressure: float) -> str:
        notes = []
        if environment_pressure > 0.5:
            notes.append("外部環境の圧力が強く、企業に変化を強いている")
        if sum(abs(v) for v in culture_shift.values()) > 0.1:
            notes.append("文化が大きくシフトしている")
        if sum(abs(v) for v in leadership_shift.values()) > 0.1:
            notes.append("経営チームの判断基準が変化している")
        return "; ".join(notes) if notes else "安定した進化"