import os
import json
from typing import List, Dict, Optional
from .scenario_engine import ScenarioEngine
from ..models.scenario_model import ScenarioResult
from .culture_service import CultureService
from .external_environment_service_v2 import ExternalEnvironmentServiceV2
from .financial_service import FinancialService


class ScenarioService:
    """シナリオ計画サービス"""

    def __init__(self):
        self.engine = ScenarioEngine()
        self.scenarios_dir = os.path.join(os.path.dirname(__file__), '../../../data/scenarios')
        os.makedirs(self.scenarios_dir, exist_ok=True)

    def run_all_scenarios(self) -> List[ScenarioResult]:
        """全シナリオを実行し、結果を保存"""
        # 現在の culture / environment / executive team を取得
        current_culture = self._get_current_culture()
        current_environment = self._get_current_environment()
        current_executive_team = self._get_current_executive_team()
        current_financials = self._get_current_financials()

        # シナリオ定義を取得
        scenario_definitions = self.engine.generate_scenario_definitions()

        results = []
        for scenario_def in scenario_definitions:
            # 各シナリオを実行
            result = self.engine.run_scenario(
                scenario_def,
                current_culture,
                current_environment,
                current_executive_team,
                current_financials
            )
            results.append(result)

            # /data/scenarios/{scenario_type}.json に保存
            self._save_scenario_result(result)

        return results

    def get_scenario_result(self, scenario_type: str) -> Optional[ScenarioResult]:
        """指定シナリオの結果を取得"""
        file_path = os.path.join(self.scenarios_dir, f'{scenario_type}.json')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ScenarioResult(**data)
        return None

    def get_all_scenario_results(self) -> List[ScenarioResult]:
        """全シナリオ結果を取得"""
        results = []
        for scenario_type in ['baseline', 'optimistic', 'pessimistic', 'tech_boom', 'recession']:
            result = self.get_scenario_result(scenario_type)
            if result:
                results.append(result)
        return results

    def get_last_preview(self) -> Optional[Dict[str, object]]:
        """最後に保存されたシナリオ結果のプレビューを返す"""
        scenario_results = self.get_all_scenario_results()
        if not scenario_results:
            return None
        latest = scenario_results[0]
        return {
            "scenario_type": latest.scenario_type.value,
            "description": latest.description,
            "risk_assessment": latest.risk_assessment,
            "opportunity_assessment": latest.opportunity_assessment,
            "projected_evolution_score": latest.projected_evolution_score,
            "projected_financials": latest.projected_financials,
        }

    def _get_current_culture(self) -> object:
        """現在の文化を取得"""
        try:
            culture_service = CultureService()
            return culture_service.get_latest_culture()
        except:
            # デフォルト文化
            from ..models.culture_model import CultureProfile
            return CultureProfile(
                period="2026-01",
                innovation_culture=0.5,
                people_culture=0.5,
                execution_culture=0.5,
                aggressiveness_culture=0.5,
                risk_aversion_culture=0.5,
                brand_culture=0.5,
                cost_culture=0.5,
                stability_culture=0.5,
            )

    def _get_current_environment(self) -> object:
        """現在の外部環境を取得"""
        try:
            env_service = ExternalEnvironmentServiceV2()
            return env_service.get_environment("2026-01")
        except:
            # デフォルト環境
            from ..models.external_environment_model_v2 import ExternalEnvironmentState, PESTFactors, CompetitorAction
            return ExternalEnvironmentState(
                period="2026-01",
                pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.5),
                competitors=[CompetitorAction(competitor_name="Competitor A", aggressiveness=0.5, market_share_shift=0.3)],
                shocks=[],
                market_growth_modifier=0.02,
                risk_modifier=0.0
            )

    def _get_current_executive_team(self) -> Dict[str, object]:
        """現在の経営チームを取得"""
        # 簡易実装: 空のDictを返す
        return {}

    def _get_current_financials(self) -> Dict[str, float]:
        """現在の財務を取得"""
        try:
            financial_service = FinancialService()
            financials = financial_service.load_financials()
            return {
                'revenue': financials.free_cash_flow * 12,  # 推定
                'profit': financials.free_cash_flow,
                'cash': financials.cash_reserves
            }
        except:
            return {
                'revenue': 1000000,
                'profit': 100000,
                'cash': 5000000
            }

    def _save_scenario_result(self, result: ScenarioResult):
        """シナリオ結果を保存"""
        file_path = os.path.join(self.scenarios_dir, f'{result.scenario_type.value}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
