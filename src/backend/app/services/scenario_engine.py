from typing import List, Dict
from ..models.scenario_model import ScenarioType, ScenarioDefinition, ScenarioResult
from ..models.culture_model import CultureProfile
from ..models.external_environment_model_v2 import ExternalEnvironmentState


class ScenarioEngine:
    """未来予測シナリオ生成エンジン"""

    def generate_scenario_definitions(self) -> List[ScenarioDefinition]:
        """標準シナリオ定義を生成"""
        return [
            ScenarioDefinition(
                scenario_type=ScenarioType.BASELINE,
                description="現状維持のベースラインシナリオ",
                duration_months=36,
                environment_modifiers={}
            ),
            ScenarioDefinition(
                scenario_type=ScenarioType.OPTIMISTIC,
                description="好況・技術進展・競合弱体化",
                duration_months=36,
                environment_modifiers={"economic": 0.1, "technological": 0.1}
            ),
            ScenarioDefinition(
                scenario_type=ScenarioType.PESSIMISTIC,
                description="不況・競合強化・消費低迷",
                duration_months=36,
                environment_modifiers={"economic": -0.15, "social": -0.1}
            ),
            ScenarioDefinition(
                scenario_type=ScenarioType.TECH_BOOM,
                description="技術革新が急進展する未来",
                duration_months=36,
                environment_modifiers={"technological": 0.25}
            ),
            ScenarioDefinition(
                scenario_type=ScenarioType.RECESSION,
                description="深刻な不況シナリオ",
                duration_months=36,
                environment_modifiers={"economic": -0.3}
            ),
        ]

    def run_scenario(
        self,
        scenario: ScenarioDefinition,
        current_culture: CultureProfile,
        current_environment: ExternalEnvironmentState,
        current_executive_team: Dict[str, object],
        current_financials: Dict[str, float]
    ) -> ScenarioResult:
        """シナリオを実行し、未来予測結果を生成"""

        # 外部環境の未来予測
        projected_environment = self._project_environment(current_environment, scenario.environment_modifiers)

        # 文化の未来予測
        projected_culture = self._project_culture(current_culture, projected_environment)

        # 経営チームの未来予測
        projected_executive_team = self._project_executive_team(current_executive_team, projected_environment)

        # 財務予測
        projected_financials = self._project_financials(current_financials, projected_environment, scenario.duration_months)

        # 進化スコア予測
        projected_evolution_score = self._project_evolution_score(projected_culture, projected_executive_team, projected_environment)

        # リスク・機会評価
        risk_assessment, opportunity_assessment = self._assess_risks_and_opportunities(scenario.scenario_type, projected_environment)

        return ScenarioResult(
            scenario_type=scenario.scenario_type,
            projected_culture=projected_culture,
            projected_executive_team=projected_executive_team,
            projected_financials=projected_financials,
            projected_evolution_score=projected_evolution_score,
            risk_assessment=risk_assessment,
            opportunity_assessment=opportunity_assessment
        )

    def _project_environment(self, current_env: ExternalEnvironmentState, modifiers: Dict[str, float]) -> ExternalEnvironmentState:
        """外部環境の未来予測"""
        # 簡易実装: modifier を加算
        new_pest = current_env.pest.model_copy()
        if 'economic' in modifiers:
            new_pest.economic = min(1.0, max(0.0, new_pest.economic + modifiers['economic']))
        if 'technological' in modifiers:
            new_pest.technological = min(1.0, max(0.0, new_pest.technological + modifiers['technological']))
        if 'social' in modifiers:
            new_pest.social = min(1.0, max(0.0, new_pest.social + modifiers['social']))

        # 競合 aggressiveness の変動
        new_competitors = []
        for comp in current_env.competitors:
            new_aggressiveness = comp.aggressiveness
            if 'economic' in modifiers and modifiers['economic'] < 0:
                new_aggressiveness = min(1.0, new_aggressiveness + 0.05)  # 不況で競合が強くなる
            new_competitors.append(comp.model_copy(update={'aggressiveness': new_aggressiveness}))

        # market_growth_modifier の再計算
        market_growth_modifier = current_env.market_growth_modifier
        if 'economic' in modifiers:
            market_growth_modifier += modifiers['economic'] * 0.5

        return current_env.model_copy(update={
            'pest': new_pest,
            'competitors': new_competitors,
            'market_growth_modifier': market_growth_modifier
        })

    def _project_culture(self, current_culture: CultureProfile, projected_env: ExternalEnvironmentState) -> CultureProfile:
        """文化の未来予測"""
        new_culture = current_culture.model_copy()

        # 技術進展 → innovation_culture +0.05
        if projected_env.pest.technological > current_culture.innovation_culture:
            new_culture.innovation_culture = min(1.0, new_culture.innovation_culture + 0.05)

        # 不況 → stability_culture +0.05
        if projected_env.pest.economic < 0.4:
            new_culture.stability_culture = min(1.0, new_culture.stability_culture + 0.05)

        # 競合 aggressiveness → aggressiveness_culture +0.03
        avg_competitor_aggressiveness = sum(c.aggressiveness for c in projected_env.competitors) / len(projected_env.competitors)
        if avg_competitor_aggressiveness > 0.6:
            new_culture.aggressiveness_culture = min(1.0, new_culture.aggressiveness_culture + 0.03)

        return new_culture

    def _project_executive_team(self, current_team: Dict[str, object], projected_env: ExternalEnvironmentState) -> Dict[str, object]:
        """経営チームの未来予測"""
        # 簡易実装: 基本的に変化なし、環境に応じて一部調整
        new_team = current_team.copy()

        # CFO: economic が悪化 → risk_tolerance -0.05 (簡易表現)
        # CMO: tech が上昇 → innovation_bias +0.05 (簡易表現)
        # COO: market_growth_modifier が低下 → operational_focus +0.05 (簡易表現)

        # 実際の ExecutivePersona モデルがないので、Dict のまま
        return new_team

    def _project_financials(self, current_financials: Dict[str, float], projected_env: ExternalEnvironmentState, duration_months: int) -> Dict[str, float]:
        """財務予測"""
        current_revenue = current_financials.get('revenue', 1000000)
        current_profit = current_financials.get('profit', 100000)
        current_cash = current_financials.get('cash', 5000000)

        # revenue = current_revenue × (1 + market_growth_modifier × 年数)
        years = duration_months / 12
        revenue_growth = projected_env.market_growth_modifier * years
        projected_revenue = current_revenue * (1 + revenue_growth)

        # profit = revenue × margin (margin は現在の profit/revenue を維持)
        margin = current_profit / current_revenue if current_revenue > 0 else 0.1
        projected_profit = projected_revenue * margin

        # cash = previous_cash + accumulated_profit (簡易)
        projected_cash = current_cash + (projected_profit * years)

        return {
            'revenue': projected_revenue,
            'profit': projected_profit,
            'cash': projected_cash
        }

    def _project_evolution_score(self, projected_culture: CultureProfile, projected_team: Dict[str, object], projected_env: ExternalEnvironmentState) -> float:
        """進化スコア予測"""
        # 簡易計算: 文化の平均 + 環境の経済 + 技術
        culture_avg = (projected_culture.innovation_culture + projected_culture.aggressiveness_culture + projected_culture.stability_culture) / 3
        env_score = (projected_env.pest.economic + projected_env.pest.technological) / 2
        return (culture_avg + env_score) / 2

    def _assess_risks_and_opportunities(self, scenario_type: ScenarioType, projected_env: ExternalEnvironmentState) -> tuple[str, str]:
        """リスク・機会評価"""
        if scenario_type == ScenarioType.RECESSION:
            risk = "High"
            opportunity = "Low"
        elif scenario_type == ScenarioType.TECH_BOOM:
            risk = "Medium"
            opportunity = "High"
        elif scenario_type == ScenarioType.OPTIMISTIC:
            risk = "Low"
            opportunity = "High"
        elif scenario_type == ScenarioType.PESSIMISTIC:
            risk = "High"
            opportunity = "Low"
        else:  # BASELINE
            risk = "Medium"
            opportunity = "Medium"

        return risk, opportunity
