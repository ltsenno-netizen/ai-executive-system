import json
import os
from typing import List, Optional

from ..models.culture_model import CultureProfile
from ..models.ai_ceo_model import AICeoPersona
from ..models.executive_meeting_model import BoardDecision
from ..models.external_environment_model_v2 import ExternalEnvironmentState
from ..models.quarterly_review_model import QuarterlyReview
from .culture_engine import CultureEngine
from .ceo_learning_service import CeoLearningService
from .executive_meeting_service import ExecutiveMeetingService
from .quarterly_review_service import QuarterlyReviewService


class CultureService:
    def __init__(self, culture_root: Optional[str] = None):
        self.engine = CultureEngine()
        self.ceo_learning_service = CeoLearningService()
        self.meeting_service = ExecutiveMeetingService()
        self.quarterly_review_service = QuarterlyReviewService()
        self.culture_root = culture_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/culture')
        )
        os.makedirs(self.culture_root, exist_ok=True)

    def update_and_store_culture(self, period: str, environment: Optional[ExternalEnvironmentState] = None) -> CultureProfile:
        """
        1. 前月文化を取得（なければ初期値）
        2. CEO Persona を取得
        3. Board 決定を取得
        4. 四半期レビュー（該当する場合）を取得
        5. culture_engine.update_culture を呼ぶ
        6. /data/culture/{period}.json に保存
        7. CultureProfile を返す
        """
        # 前月文化を取得
        previous_culture = self.get_latest_culture()

        # CEO Persona を取得
        try:
            ceo_persona = self.ceo_learning_service.get_latest_persona()
            if ceo_persona is None:
                ceo_persona = self.ceo_learning_service._get_base_persona()
        except Exception:
            ceo_persona = self.ceo_learning_service._get_base_persona()

        # Board 決定を取得
        try:
            # 直近の meeting state から board_decision を取得
            board_decisions = self._get_recent_board_decisions(period)
        except Exception:
            board_decisions = []

        # 四半期レビューを取得
        quarterly_review = None
        try:
            # 該当する四半期があれば取得
            year, month = map(int, period.split('-'))
            if month % 3 == 0:  # 3月、6月、9月、12月
                quarter_num = month // 3
                quarter = f"{year}-Q{quarter_num}"
                quarterly_review = self.quarterly_review_service.get_quarterly_review(quarter)
        except Exception:
            quarterly_review = None

        # 文化を更新
        updated_culture_dict = self.engine.update_culture(
            previous_culture=previous_culture,
            ceo_persona=ceo_persona,
            board_decisions=board_decisions,
            quarterly_review=quarterly_review,
            environment=environment,
        )

        # CultureProfile として作成
        culture_profile = CultureProfile(
            period=period,
            aggressiveness_culture=updated_culture_dict['aggressiveness_culture'],
            risk_aversion_culture=updated_culture_dict['risk_aversion_culture'],
            brand_culture=updated_culture_dict['brand_culture'],
            cost_culture=updated_culture_dict['cost_culture'],
            people_culture=updated_culture_dict['people_culture'],
            execution_culture=updated_culture_dict['execution_culture'],
            innovation_culture=updated_culture_dict['innovation_culture'],
            stability_culture=updated_culture_dict['stability_culture'],
            notes=f"Updated on {period} with CEO persona, board decisions, and quarterly performance.",
        )

        # 保存
        self._save_culture(culture_profile)

        return culture_profile

    def get_latest_culture(self) -> Optional[CultureProfile]:
        """最新の文化プロファイルを取得"""
        files = [f for f in os.listdir(self.culture_root) if f.endswith('.json')]
        if not files:
            return None
        files.sort()
        latest_file = files[-1]
        return self._load_culture(latest_file)

    def get_culture_for_period(self, period: str) -> Optional[CultureProfile]:
        """指定期間の文化プロファイルを取得"""
        path = os.path.join(self.culture_root, f'{period}.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return CultureProfile(**data)
            except Exception:
                return None
        return None

    def get_culture_history(self, periods: int = 12) -> List[CultureProfile]:
        """文化の履歴を取得（直近N期間）"""
        files = sorted([f for f in os.listdir(self.culture_root) if f.endswith('.json')], reverse=True)[:periods]
        history = []
        for filename in sorted(files):
            try:
                culture = self._load_culture(filename)
                if culture:
                    history.append(culture)
            except Exception:
                pass
        return sorted(history, key=lambda c: c.period)

    def _get_recent_board_decisions(self, period: str) -> List[BoardDecision]:
        """直近の Board 決定を取得"""
        try:
            state = self.meeting_service.load_latest_state_for_month(int(period.split('-')[1]))
            if state and hasattr(state, 'board_decision') and state.board_decision:
                return [state.board_decision]
            return []
        except Exception:
            return []

    def _save_culture(self, culture_profile: CultureProfile) -> None:
        """文化プロファイルを保存"""
        path = os.path.join(self.culture_root, f'{culture_profile.period}.json')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(culture_profile.model_dump_json(indent=2, ensure_ascii=False))

    def _load_culture(self, filename: str) -> CultureProfile:
        """ファイルから文化プロファイルを読み込む"""
        path = os.path.join(self.culture_root, filename)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return CultureProfile(**data)
