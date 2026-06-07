from datetime import datetime
from typing import Dict, List, Optional

from ..models.scenario_simulation_model import ScenarioSimulationDefinition, ScenarioSimulationResult
from ..models.culture_model import CultureProfile
from ..models.external_environment_model_v2 import ExternalEnvironmentState, MarketShock
from ..models.corporate_consciousness_evolution_model import (
    ConsciousnessEvolutionEvent,
    ConsciousnessEvolutionState,
    EvolutionTriggerType,
    ConsciousnessPhase,
)
from ..models.scenario_model import ScenarioType


class ScenarioSimulationEngine:
    """Future scenario simulation engine for Step AJ"""

    def generate_simulation_definitions(self) -> List[ScenarioSimulationDefinition]:
        """Generate a set of future simulation definitions."""
        return [
            ScenarioSimulationDefinition(
                scenario_type=ScenarioType.BASELINE,
                description="現状維持の未来シナリオ",
                duration_months=36,
                environment_modifiers={"economic": 0.0, "technological": 0.0, "social": 0.0},
                scenario_drivers={"focus": "stability"},
                stress_factors={"regulatory": 0.0, "supply_chain": 0.0},
                narrative_focus="現状の環境トレンドをベースにした予測",
                confidence_adjustment=0.0,
            ),
            ScenarioSimulationDefinition(
                scenario_type=ScenarioType.OPTIMISTIC,
                description="成長機会が開く楽観シナリオ",
                duration_months=36,
                environment_modifiers={"economic": 0.12, "technological": 0.15, "social": 0.05},
                scenario_drivers={"focus": "innovation"},
                stress_factors={"regulatory": 0.0, "supply_chain": 0.0},
                narrative_focus="技術革新と市場拡大が優勢となる未来",
                confidence_adjustment=0.05,
            ),
            ScenarioSimulationDefinition(
                scenario_type=ScenarioType.PESSIMISTIC,
                description="リスクが顕在化する悲観シナリオ",
                duration_months=36,
                environment_modifiers={"economic": -0.2, "social": -0.1},
                scenario_drivers={"focus": "risk_management"},
                stress_factors={"regulatory": 0.2, "supply_chain": 0.15},
                narrative_focus="景況感悪化と規制・サプライチェーンリスクが重なる未来",
                confidence_adjustment=-0.05,
            ),
            ScenarioSimulationDefinition(
                scenario_type=ScenarioType.TECH_BOOM,
                description="技術大躍進による変革シナリオ",
                duration_months=36,
                environment_modifiers={"technological": 0.3, "economic": 0.08},
                scenario_drivers={"focus": "disruption"},
                stress_factors={"regulatory": 0.0, "supply_chain": 0.0},
                narrative_focus="デジタル変革と新技術の採用が急進展する未来",
                confidence_adjustment=0.08,
            ),
            ScenarioSimulationDefinition(
                scenario_type=ScenarioType.RECESSION,
                description="深刻な景気後退シナリオ",
                duration_months=36,
                environment_modifiers={"economic": -0.35, "technological": -0.05},
                scenario_drivers={"focus": "cost_control"},
                stress_factors={"regulatory": 0.1, "supply_chain": 0.1},
                narrative_focus="消費縮小とコスト圧力が強まる未来",
                confidence_adjustment=-0.1,
            ),
        ]

    def run_simulation(
        self,
        definition: ScenarioSimulationDefinition,
        current_culture: CultureProfile,
        current_environment: ExternalEnvironmentState,
        current_evolution_state: Optional[ConsciousnessEvolutionState],
        current_financials: Dict[str, float],
    ) -> ScenarioSimulationResult:
        """Run one future scenario simulation."""
        projected_environment = self._project_environment(
            current_environment,
            definition.environment_modifiers,
            definition.stress_factors,
        )

        projected_culture = self._project_culture(current_culture, projected_environment, definition.scenario_drivers)
        projected_evolution = self._project_consciousness_evolution(
            current_evolution_state,
            projected_environment,
            projected_culture,
            definition,
        )
        financial_summary = self._project_financial_impact(
            current_financials,
            projected_environment,
            projected_culture,
            definition.duration_months,
            definition.scenario_type,
        )
        scenario_score = self._score_scenario(
            projected_culture,
            projected_environment,
            projected_evolution,
            financial_summary,
            definition,
        )
        risk_assessment, opportunity_assessment = self._assess_risk_opportunity(
            definition.scenario_type,
            projected_environment,
        )
        return ScenarioSimulationResult(
            scenario_type=definition.scenario_type,
            description=definition.description,
            duration_months=definition.duration_months,
            scenario_drivers=definition.scenario_drivers,
            stress_factors=definition.stress_factors,
            narrative_focus=definition.narrative_focus,
            projected_environment=projected_environment,
            projected_culture=projected_culture,
            projected_consciousness_evolution=projected_evolution,
            financial_impact_summary=financial_summary,
            risk_assessment=risk_assessment,
            opportunity_assessment=opportunity_assessment,
            scenario_score=scenario_score,
            confidence=max(0.0, min(1.0, 0.65 + definition.confidence_adjustment + (scenario_score - 0.5) * 0.2)),
            contingency_recommendations=self._recommend_actions(definition, projected_environment, projected_culture),
            strategic_implications=self._build_strategic_implications(definition, projected_environment, projected_culture),
        )

    def _project_environment(
        self,
        current_env: ExternalEnvironmentState,
        modifiers: Dict[str, float],
        stress_factors: Dict[str, float],
    ) -> ExternalEnvironmentState:
        new_pest = current_env.pest.model_copy()
        for key, delta in modifiers.items():
            if hasattr(new_pest, key):
                setattr(new_pest, key, min(1.0, max(0.0, getattr(new_pest, key) + delta)))

        regulator_impact = stress_factors.get("regulatory", 0.0)
        supply_impact = stress_factors.get("supply_chain", 0.0)

        if regulator_impact > 0:
            new_pest.political = max(0.0, new_pest.political - regulator_impact * 0.15)
        if supply_impact > 0:
            new_pest.economic = max(0.0, new_pest.economic - supply_impact * 0.1)

        new_competitors = []
        for comp in current_env.competitors:
            adjustment = 0.0
            if modifiers.get("economic", 0.0) < 0:
                adjustment += 0.05
            if stress_factors.get("supply_chain", 0.0) > 0.1:
                adjustment += 0.03
            new_competitors.append(comp.model_copy(update={
                "aggressiveness": min(1.0, max(0.0, comp.aggressiveness + adjustment))
            }))

        market_growth_modifier = current_env.market_growth_modifier + modifiers.get("economic", 0.0) * 0.5
        market_growth_modifier -= supply_impact * 0.05

        shocks = list(current_env.shocks)
        if stress_factors.get("regulatory", 0.0) > 0.1:
            shocks.append(
                MarketShock(
                    shock_type="regulatory",
                    severity=min(1.0, regulator_impact),
                    duration_months=12,
                    description="Regulatory tightening impacts growth and risk appetite",
                )
            )
        if stress_factors.get("supply_chain", 0.0) > 0.1:
            shocks.append(
                MarketShock(
                    shock_type="supply_chain",
                    severity=min(1.0, supply_impact),
                    duration_months=9,
                    description="Supply chain disruption slows market performance",
                )
            )

        return current_env.model_copy(update={
            "pest": new_pest,
            "competitors": new_competitors,
            "market_growth_modifier": max(-0.5, min(0.5, market_growth_modifier)),
            "risk_modifier": min(1.0, max(-1.0, current_env.risk_modifier + regulator_impact * 0.2)),
            "shocks": shocks,
        })

    def _project_culture(
        self,
        current_culture: CultureProfile,
        projected_env: ExternalEnvironmentState,
        scenario_drivers: Dict[str, str],
    ) -> CultureProfile:
        updated_culture = current_culture.model_copy()

        if projected_env.pest.technological > current_culture.innovation_culture:
            updated_culture.innovation_culture = min(1.0, updated_culture.innovation_culture + 0.06)
        if projected_env.pest.economic < 0.4:
            updated_culture.stability_culture = min(1.0, updated_culture.stability_culture + 0.05)
        if projected_env.pest.political < 0.4:
            updated_culture.risk_aversion_culture = min(1.0, updated_culture.risk_aversion_culture + 0.04)
        if projected_env.pest.social < 0.4:
            updated_culture.people_culture = min(1.0, updated_culture.people_culture + 0.03)

        focus = scenario_drivers.get("focus", "")
        if focus == "innovation":
            updated_culture.innovation_culture = min(1.0, updated_culture.innovation_culture + 0.05)
        elif focus == "cost_control":
            updated_culture.execution_culture = min(1.0, updated_culture.execution_culture + 0.04)
        elif focus == "risk_management":
            updated_culture.risk_aversion_culture = min(1.0, updated_culture.risk_aversion_culture + 0.05)

        avg_competitor_aggressiveness = sum(c.aggressiveness for c in projected_env.competitors) / max(1, len(projected_env.competitors))
        if avg_competitor_aggressiveness > 0.6:
            updated_culture.aggressiveness_culture = min(1.0, updated_culture.aggressiveness_culture + 0.03)

        return updated_culture

    def _project_consciousness_evolution(
        self,
        current_state: Optional[ConsciousnessEvolutionState],
        projected_env: ExternalEnvironmentState,
        projected_culture: CultureProfile,
        definition: ScenarioSimulationDefinition,
    ) -> ConsciousnessEvolutionState:
        if current_state is None:
            current_state = ConsciousnessEvolutionState()

        momentum_delta = 0.0
        stability_delta = 0.0
        trigger_type = EvolutionTriggerType.EXTERNAL_SHOCK
        reason = "環境変化により意識進化が促進される"

        if definition.scenario_type == ScenarioType.OPTIMISTIC:
            momentum_delta += 0.08
            stability_delta += 0.04
            trigger_type = EvolutionTriggerType.STRATEGY_SHIFT
            reason = "成長機会に対応するための意識変革"
        elif definition.scenario_type == ScenarioType.PESSIMISTIC:
            momentum_delta += 0.12
            stability_delta -= 0.08
            trigger_type = EvolutionTriggerType.EXTERNAL_SHOCK
            reason = "逆境対応で自己認識が再検討される"
        elif definition.scenario_type == ScenarioType.TECH_BOOM:
            momentum_delta += 0.10
            stability_delta += 0.03
            trigger_type = EvolutionTriggerType.CULTURE_SHIFT
            reason = "技術イノベーションが組織意識を刺激する"
        elif definition.scenario_type == ScenarioType.RECESSION:
            momentum_delta += 0.05
            stability_delta += 0.10
            trigger_type = EvolutionTriggerType.PERFORMANCE_BREAKPOINT
            reason = "リスク低減へ向けた意識の再構築"

        if projected_env.market_growth_modifier < 0:
            stability_delta += 0.02
        if projected_env.risk_modifier > 0.2:
            momentum_delta += 0.05

        next_phase = current_state.current_phase
        if momentum_delta > 0.1 and current_state.momentum > 0.5:
            next_phase = ConsciousnessPhase.TRANSFORMING
        elif momentum_delta < -0.05:
            next_phase = ConsciousnessPhase.CONSOLIDATING

        updated_state = current_state.model_copy(update={
            "current_phase": next_phase,
            "momentum": min(1.0, max(0.0, current_state.momentum + momentum_delta)),
            "stability": min(1.0, max(0.0, current_state.stability + stability_delta)),
            "last_update": datetime.now(),
        })

        event = ConsciousnessEvolutionEvent(
            event_id=f"scenario-{definition.scenario_type.value}-{int(datetime.now().timestamp())}",
            trigger_type=trigger_type,
            description=reason,
            impact_on_identity=0.02 if definition.scenario_type == ScenarioType.OPTIMISTIC else -0.03,
            impact_on_purpose=0.03 if definition.scenario_type == ScenarioType.TECH_BOOM else -0.02,
            impact_on_direction=0.04 if definition.scenario_type == ScenarioType.OPTIMISTIC else 0.0,
            impact_on_risk_posture=-0.02 if definition.scenario_type == ScenarioType.RECESSION else 0.01,
        )

        history = list(current_state.history)
        history.append(event)
        updated_state.history = history[-20:]

        return updated_state

    def _project_financial_impact(
        self,
        current_financials: Dict[str, float],
        projected_env: ExternalEnvironmentState,
        projected_culture: CultureProfile,
        duration_months: int,
        scenario_type: ScenarioType,
    ) -> Dict[str, float]:
        current_revenue = current_financials.get("revenue", 1000000)
        current_profit = current_financials.get("profit", 100000)
        current_cash = current_financials.get("cash", 5000000)
        years = duration_months / 12

        multiplier = 1.0 + projected_env.market_growth_modifier * years
        if scenario_type == ScenarioType.PESSIMISTIC:
            multiplier *= 0.85
        elif scenario_type == ScenarioType.RECESSION:
            multiplier *= 0.75
        elif scenario_type == ScenarioType.TECH_BOOM:
            multiplier *= 1.15

        projected_revenue = max(0.0, current_revenue * multiplier)
        margin = current_profit / current_revenue if current_revenue > 0 else 0.1
        projected_profit = max(0.0, projected_revenue * margin)
        projected_cash = max(0.0, current_cash + projected_profit * years)

        return {
            "revenue": projected_revenue,
            "profit": projected_profit,
            "cash": projected_cash,
            "growth_rate": projected_env.market_growth_modifier,
            "operating_margin": margin,
        }

    def _score_scenario(
        self,
        projected_culture: CultureProfile,
        projected_environment: ExternalEnvironmentState,
        projected_evolution: ConsciousnessEvolutionState,
        financial_summary: Dict[str, float],
        definition: ScenarioSimulationDefinition,
    ) -> float:
        culture_score = (
            projected_culture.innovation_culture
            + projected_culture.aggressiveness_culture
            + projected_culture.stability_culture
        ) / 3
        env_score = (projected_environment.pest.economic + projected_environment.pest.technological + (1.0 - projected_environment.risk_modifier)) / 3
        evolution_score = (projected_evolution.momentum + projected_evolution.stability) / 2
        financial_score = min(1.0, max(0.0, financial_summary.get("revenue", 0) / (1_000_000 * (1 + projected_environment.market_growth_modifier))))

        score = (culture_score * 0.3) + (env_score * 0.25) + (evolution_score * 0.2) + (financial_score * 0.25)
        return min(1.0, max(0.0, score))

    def _recommend_actions(
        self,
        definition: ScenarioSimulationDefinition,
        projected_environment: ExternalEnvironmentState,
        projected_culture: CultureProfile,
    ) -> List[str]:
        recommendations = []
        if definition.scenario_type == ScenarioType.OPTIMISTIC:
            recommendations.extend([
                "イノベーション投資を継続し、市場拡大の機会を活用する",
                "技術ロードマップを明確化し、変化に対応する組織能力を強化する",
            ])
        elif definition.scenario_type == ScenarioType.PESSIMISTIC:
            recommendations.extend([
                "コスト構造を見直し、耐久性の高いオペレーションを構築する",
                "市場の需要低下に備えた代替成長シナリオを準備する",
            ])
        elif definition.scenario_type == ScenarioType.TECH_BOOM:
            recommendations.extend([
                "イノベーション主導の事業開発を加速する",
                "デジタルトランスフォーメーションと人材育成を同時に進める",
            ])
        elif definition.scenario_type == ScenarioType.RECESSION:
            recommendations.extend([
                "安全性の高い資金調達とキャッシュ保全を優先する",
                "収益性の高いコア事業に集中し、投資を慎重化する",
            ])
        else:
            recommendations.append("現状のシナリオを定期的に見直し、変化に応じた対応策を更新する")

        if projected_environment.pest.political < 0.4:
            recommendations.append("政治リスクに備えたガバナンス強化を実施する")
        if projected_environment.pest.economic < 0.3:
            recommendations.append("不況期の需要変動に対応する代替戦略を策定する")

        return recommendations

    def _build_strategic_implications(
        self,
        definition: ScenarioSimulationDefinition,
        projected_environment: ExternalEnvironmentState,
        projected_culture: CultureProfile,
    ) -> List[str]:
        implications = [
            f"{definition.description} の場合、経営チームは意思決定の柔軟性を高める必要があります。",
            f"市場成長率は {projected_environment.market_growth_modifier:.2f} 付近で推移すると予測されます。",
        ]
        if projected_culture.stability_culture > 0.7:
            implications.append("文化的に安定感が高まるため、長期投資に踏み切りやすい。")
        if projected_environment.risk_modifier > 0.2:
            implications.append("リスク管理を強化し、外部ショックに備える必要がある。")
        return implications

    def _assess_risk_opportunity(self, scenario_type: ScenarioType, projected_environment: ExternalEnvironmentState) -> tuple[str, str]:
        if scenario_type == ScenarioType.RECESSION:
            return "High", "Low"
        if scenario_type == ScenarioType.PESSIMISTIC:
            return "High", "Medium"
        if scenario_type == ScenarioType.TECH_BOOM:
            return "Medium", "High"
        if scenario_type == ScenarioType.OPTIMISTIC:
            return "Low", "High"
        return "Medium", "Medium"
