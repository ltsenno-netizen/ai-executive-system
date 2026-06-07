import os
import json
from typing import List, Dict, Optional
from .self_optimization_engine import build_self_optimization_plan
from ..models.self_optimization_model import OptimizationObjective, SelfOptimizationPlan
from ..models.scenario_model import ScenarioResult
from .scenario_service import ScenarioService
from .culture_service import CultureService
from .financial_service import FinancialService


class SelfOptimizationService:
    """自己最適化プラン生成サービス"""

    def __init__(self):
        self.scenario_service = ScenarioService()
        self.culture_service = CultureService()
        self.financial_service = FinancialService()
        self.optimization_dir = os.path.join(
            os.path.dirname(__file__), '../../../data/self_optimization'
        )
        os.makedirs(self.optimization_dir, exist_ok=True)

    def generate_self_optimization_plan(
        self, objective: OptimizationObjective
    ) -> SelfOptimizationPlan:
        """自己最適化プランを生成し保存"""
        # 1. 最新の scenario_results を取得
        scenario_results = self.scenario_service.get_all_scenario_results()
        if not scenario_results:
            raise ValueError("No scenario results found. Run scenarios first.")

        # 2. 現在の culture / executive_team / financials を取得
        current_culture = self._get_current_culture()
        current_executive_team = self._get_current_executive_team()
        current_financials = self._get_current_financials()

        # 3. build_self_optimization_plan を実行
        plan = build_self_optimization_plan(
            objective,
            scenario_results,
            current_culture,
            current_executive_team,
            current_financials
        )

        # 4. /data/self_optimization/{objective}.json に保存
        self._save_plan(plan)

        # 5. 結果を返す
        return plan

    def get_latest_plan(self, objective: Optional[OptimizationObjective] = None) -> Optional[SelfOptimizationPlan]:
        """最新の最適化プランを取得"""
        if objective:
            file_path = os.path.join(self.optimization_dir, f'{objective.value}.json')
        else:
            # 最新ファイルを取得
            files = os.listdir(self.optimization_dir)
            if not files:
                return None
            latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(self.optimization_dir, f)))
            file_path = os.path.join(self.optimization_dir, latest_file)

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return SelfOptimizationPlan(**data)
        return None

    def get_all_plans(self) -> List[SelfOptimizationPlan]:
        """すべての最適化プランを取得"""
        plans = []
        if os.path.exists(self.optimization_dir):
            for file_name in os.listdir(self.optimization_dir):
                if file_name.endswith('.json'):
                    file_path = os.path.join(self.optimization_dir, file_name)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        plans.append(SelfOptimizationPlan(**data))
        return plans

    def _get_current_culture(self) -> Dict:
        """現在の企業文化を取得"""
        try:
            culture = self.culture_service.get_latest_culture()
            return culture if culture else {}
        except Exception:
            return {}

    def _get_current_executive_team(self) -> Dict:
        """現在の経営チームを取得"""
        # TODO: 実装に応じて修正
        return {
            "CEO": {"aggressiveness": 0.5, "risk_tolerance": 0.5, "brand_priority": 0.5},
            "CFO": {"aggressiveness": 0.4, "risk_tolerance": 0.3, "brand_priority": 0.4},
            "CMO": {"aggressiveness": 0.6, "risk_tolerance": 0.6, "brand_priority": 0.7},
        }

    def _get_current_financials(self) -> Dict[str, float]:
        """現在の財務状況を取得"""
        try:
            financials = self.financial_service.get_current_financials()
            return financials if financials else {"revenue": 100.0, "profit": 10.0, "cash": 50.0}
        except Exception:
            return {"revenue": 100.0, "profit": 10.0, "cash": 50.0}

    def _save_plan(self, plan: SelfOptimizationPlan) -> None:
        """プランをJSONで保存"""
        file_path = os.path.join(self.optimization_dir, f'{plan.objective.value}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(plan.model_dump(), f, ensure_ascii=False, indent=2)
