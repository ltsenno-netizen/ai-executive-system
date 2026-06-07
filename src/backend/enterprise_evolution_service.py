import json
import os
from typing import Dict, List, Optional

from enterprise_evolution_engine import EnterpriseEvolutionEngine, EnterpriseEvolutionResult
from app.models.culture_model import CultureProfile
from app.models.external_environment_model_v2 import ExternalEnvironmentState
from executive_team_succession_model import ExecutivePersona, ExecutiveRole
from app.models.executive_meeting_model import BoardDecision
from app.services.culture_service import CultureService
from app.services.external_environment_service_v2 import ExternalEnvironmentServiceV2


class EnterpriseEvolutionService:
    def __init__(self):
        self.engine = EnterpriseEvolutionEngine()
        self.culture_service = CultureService()
        self.environment_service = ExternalEnvironmentServiceV2()
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'evolution')
        os.makedirs(self.data_dir, exist_ok=True)

    def run_enterprise_evolution(self, period: str) -> EnterpriseEvolutionResult:
        # 1. 最新 culture を取得
        culture = self.culture_service.get_latest_culture()

        # 2. 最新 environment を取得
        environment = self._get_current_environment()

        # 3. 最新 executive team を取得
        executive_team = self._get_current_executive_team()

        # 4. 最新 board decisions を取得
        board_decisions = self._get_recent_board_decisions(period)

        # 5. evolution_engine.compute_enterprise_evolution を呼ぶ
        result = self.engine.compute_enterprise_evolution(
            culture, environment, executive_team, board_decisions
        )
        result.period = period

        # 6. /data/evolution/{period}.json に保存
        self._save_evolution_result(result)

        # 7. 結果を返す
        return result

    def get_evolution_result(self, period: str) -> Optional[EnterpriseEvolutionResult]:
        file_path = os.path.join(self.data_dir, f"{period}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return EnterpriseEvolutionResult(**data)
        return None

    def get_latest_evolution_result(self) -> Optional[EnterpriseEvolutionResult]:
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        if not files:
            return None
        latest_file = max(files, key=lambda x: x.split('.')[0])
        period = latest_file.split('.')[0]
        return self.get_evolution_result(period)

    def _get_current_executive_team(self) -> Dict[ExecutiveRole, ExecutivePersona]:
        # Placeholder: Implement actual retrieval
        # For now, return default team
        return {
            role: ExecutivePersona(
                role=role,
                financial_focus=0.5,
                operational_focus=0.5,
                brand_focus=0.5,
                people_focus=0.5,
                risk_tolerance=0.5,
                innovation_bias=0.5,
            ) for role in ExecutiveRole
        }

    def _get_recent_board_decisions(self, period: str) -> List[BoardDecision]:
        # Placeholder: Implement actual retrieval
        # For now, return empty list
        return []

    def _get_current_environment(self) -> ExternalEnvironmentState:
        # Placeholder: Implement actual retrieval
        # For now, return default environment
        from app.models.external_environment_model_v2 import PESTFactors, CompetitorAction, MarketShock
        return ExternalEnvironmentState(
            period="2026-01",
            pest=PESTFactors(economic=0.5, political=0.5, social=0.5, technological=0.5),
            competitors=[],
            shocks=[],
            market_growth_modifier=0.0,
            risk_modifier=0.5
        )

    def _save_evolution_result(self, result: EnterpriseEvolutionResult):
        file_path = os.path.join(self.data_dir, f"{result.period}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)