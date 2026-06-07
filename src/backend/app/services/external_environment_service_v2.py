import json
import os
from typing import Optional

from ..models.external_environment_model_v2 import ExternalEnvironmentState
from .external_environment_engine_v2 import build_external_environment_state


class ExternalEnvironmentServiceV2:
    def __init__(self, environment_root: Optional[str] = None):
        self.environment_root = environment_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/environment')
        )
        os.makedirs(self.environment_root, exist_ok=True)

    def generate_and_store_environment(self, period: str) -> ExternalEnvironmentState:
        """
        1. 前月の環境を取得
        2. build_external_environment_state を呼ぶ
        3. /data/environment/{period}.json に保存
        4. 返却
        """
        # 前月の環境を取得
        previous_state = self.get_latest_environment()

        # 新しい環境を生成
        environment = build_external_environment_state(period, previous_state)

        # 保存
        file_path = os.path.join(self.environment_root, f"{period}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(environment.model_dump(), f, ensure_ascii=False, indent=2)

        return environment

    def get_latest_environment(self) -> Optional[ExternalEnvironmentState]:
        """
        最新の環境を取得
        """
        if not os.path.exists(self.environment_root):
            return None

        files = [f for f in os.listdir(self.environment_root) if f.endswith('.json')]
        if not files:
            return None

        # 最新のファイルをソート（period が YYYY-MM 形式を仮定）
        files.sort(reverse=True)
        latest_file = files[0]
        file_path = os.path.join(self.environment_root, latest_file)

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return ExternalEnvironmentState(**data)

    def get_environment(self, period: str) -> Optional[ExternalEnvironmentState]:
        """
        指定期間の環境を取得
        """
        file_path = os.path.join(self.environment_root, f"{period}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return ExternalEnvironmentState(**data)