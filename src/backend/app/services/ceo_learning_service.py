import json
import os
from typing import List, Optional
from ..models.ceo_learning_model import CeoLearningSnapshot, FinancialResultSummary
from ..models.ai_ceo_model import AICeoPersona
from .ceo_learning_engine import CeoLearningEngine
from .executive_meeting_service import ExecutiveMeetingService
from .company_operations_integration_service import CompanyOperationsIntegrationService


class CeoLearningService:
    def __init__(self, persona_root: Optional[str] = None):
        self.engine = CeoLearningEngine()
        self.meeting_service = ExecutiveMeetingService()
        self.integration_service = CompanyOperationsIntegrationService()
        self.persona_root = persona_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../personas/ceo')
        )
        os.makedirs(self.persona_root, exist_ok=True)

    def build_learning_history(self, periods: List[str]) -> List[CeoLearningSnapshot]:
        snapshots = []
        for period in periods:
            try:
                # ceo_persona: 仮に固定で取得（後で履歴から）
                ceo_persona = self._load_persona_for_period(period) or self._get_base_persona()

                year, month = map(int, period.split('-'))
                # financial_result
                month_data = self.integration_service.simulate_month_full(month, year=year)
                financial_result = FinancialResultSummary(
                    revenue=month_data.get('financials', {}).get('revenue', 0.0),
                    operating_profit=month_data.get('financials', {}).get('operating_profit', 0.0),
                )

                # board_status
                try:
                    from .executive_meeting_service import ExecutiveMeetingService
                    state = ExecutiveMeetingService().load_meeting_state()
                    board_status = state.board_decision.status if state.board_decision else 'no_decision'
                except:
                    board_status = 'no_decision'

                snapshot = CeoLearningSnapshot(
                    period=period,
                    ceo_persona=ceo_persona,
                    financial_result=financial_result,
                    board_status=board_status,
                )
                snapshots.append(snapshot)
            except Exception as e:
                print(f"Error building snapshot for {period}: {e}")
        return snapshots

    def update_and_store_ceo_persona(self, current_period: str) -> AICeoPersona:
        # 過去 N ヶ月分の history を構築 (仮に直近6ヶ月)
        periods = [self._previous_period(current_period, i) for i in range(6, 0, -1)]
        history = self.build_learning_history(periods)

        # base_persona: 直近 or 初期
        base_persona = self.get_latest_persona() or self._get_base_persona()

        # update
        new_persona = self.engine.update_persona_from_history(base_persona, history)

        # 保存
        self._save_persona(new_persona, current_period)

        return new_persona

    def get_latest_persona(self) -> Optional[AICeoPersona]:
        candidates = []
        for filename in os.listdir(self.persona_root):
            if filename.endswith('.json'):
                base = filename[:-5]
                try:
                    # base is like '2026-01', sort by year-month
                    year, month = map(int, base.split('-'))
                    candidates.append(((year, month), filename))
                except:
                    pass
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0], reverse=True)
        return self._load_persona(candidates[0][1])

    def _load_persona_for_period(self, period: str) -> Optional[AICeoPersona]:
        path = os.path.join(self.persona_root, f'{period}.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return AICeoPersona(**data)
        return None

    def _load_persona(self, filename: str) -> AICeoPersona:
        path = os.path.join(self.persona_root, filename)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return AICeoPersona(**data)

    def _save_persona(self, persona: AICeoPersona, period: str) -> None:
        path = os.path.join(self.persona_root, f'{period}.json')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(persona.model_dump_json(indent=2, ensure_ascii=False))

    def _get_base_persona(self) -> AICeoPersona:
        # 初期パーソナ (HORIPRO_2026_PERSONA)
        return AICeoPersona(
            aggressiveness=0.6,
            risk_tolerance=0.6,
            brand_priority=0.7,
            short_term_focus=0.5,
            long_term_focus=0.8,
        )

    def _previous_period(self, period: str, months_back: int) -> str:
        year, month = map(int, period.split('-'))
        for _ in range(months_back):
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        return f"{year:04d}-{month:02d}"