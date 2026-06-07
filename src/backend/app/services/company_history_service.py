import os
import json
from typing import List, Optional
from .company_history_engine import CompanyHistoryEngine
from ..models.company_history_model import AnnualReport, CompanyHistory, LeadershipEvent
from ..models.ceo_succession_model import CeoSuccessionDecision
from ..models.executive_team_succession_model import ExecutiveSuccessionDecision
from ..models.culture_model import CultureProfile
from ..models.external_environment_model_v2 import ExternalEnvironmentState
from ..models.enterprise_evolution_model import EnterpriseEvolutionResult
from .monthly_batch_service import MonthlyBatchResult


class CompanyHistoryService:
    """企業の歴史管理サービス"""

    def __init__(self):
        self.engine = CompanyHistoryEngine()
        self.history_dir = os.path.join(os.path.dirname(__file__), '../../../data/history')
        os.makedirs(self.history_dir, exist_ok=True)

    def generate_annual_history(self, year: int) -> AnnualReport:
        """
        指定年の年次歴史を生成
        1. 対象年の monthly_results を取得
        2. 対象年の culture / environment / evolution を取得
        3. 対象年に発生した leadership_events を抽出
        4. company_history_engine.build_annual_report を呼ぶ
        5. /data/history/{year}/annual_report.json に保存
        6. AnnualReport を返す
        """
        # 月次結果取得
        monthly_results = self._load_monthly_results(year)

        # 文化履歴取得
        culture_history = self._load_culture_history(year)

        # 進化履歴取得
        evolution_history = self._load_evolution_history(year)

        # 環境履歴取得
        environment_history = self._load_environment_history(year)

        # リーダーシップイベント取得
        leadership_events = self._load_leadership_events(year)

        # 年次レポート構築
        report = self.engine.build_annual_report(
            year, monthly_results, culture_history,
            evolution_history, environment_history, leadership_events
        )

        # 保存
        year_dir = os.path.join(self.history_dir, str(year))
        os.makedirs(year_dir, exist_ok=True)
        report_path = os.path.join(year_dir, 'annual_report.json')

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)

        return report

    def generate_timeline(self) -> CompanyHistory:
        """
        完全な企業タイムラインを生成
        1. 全 CeoSuccessionDecision / ExecutiveSuccessionDecision を取得
        2. build_leadership_timeline で LeadershipEvent を生成
        3. 既存 AnnualReport を読み込み
        4. CompanyHistory を構築して返す
        """
        # CEO交代履歴取得
        ceo_successions = self._load_all_ceo_successions()

        # 経営チーム交代履歴取得
        executive_successions = self._load_all_executive_successions()

        # リーダーシップイベント構築
        leadership_events = self.engine.build_leadership_timeline(
            ceo_successions, executive_successions
        )

        # 年次レポート読み込み
        annual_reports = self._load_all_annual_reports()

        return CompanyHistory(
            leadership_events=leadership_events,
            annual_reports=annual_reports
        )

    def get_latest_annual_history(self) -> Optional[AnnualReport]:
        """最新の年次レポートを取得"""
        annual_reports = self._load_all_annual_reports()
        return max(annual_reports, key=lambda x: x.year) if annual_reports else None

    def get_annual_history(self, year: int) -> Optional[AnnualReport]:
        """指定年の年次レポートを取得"""
        year_dir = os.path.join(self.history_dir, str(year))
        report_path = os.path.join(year_dir, 'annual_report.json')

        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return AnnualReport(**data)
        return None

    # Compatibility aliases for older method names and external callers
    def get_latest_annual_report(self) -> Optional[AnnualReport]:
        return self.get_latest_annual_history()

    def get_annual_report(self, year: int) -> Optional[AnnualReport]:
        return self.get_annual_history(year)

    def get_leadership_timeline(self) -> List[LeadershipEvent]:
        """リーダーシップタイムラインを取得"""
        company_history = self.generate_timeline()
        return company_history.leadership_events

    def _load_monthly_results(self, year: int) -> List[MonthlyBatchResult]:
        """指定年の月次結果を読み込み"""
        # TODO: monthly_batch_service から取得するロジックを実装
        # 現時点では空リストを返す
        return []

    def _load_culture_history(self, year: int) -> List[CultureProfile]:
        """指定年の文化履歴を読み込み"""
        # TODO: culture_service から取得するロジックを実装
        return []

    def _load_evolution_history(self, year: int) -> List[EnterpriseEvolutionResult]:
        """指定年の進化履歴を読み込み"""
        # TODO: enterprise_evolution_service から取得するロジックを実装
        return []

    def _load_environment_history(self, year: int) -> List[ExternalEnvironmentState]:
        """指定年の環境履歴を読み込み"""
        # TODO: external_environment_service から取得するロジックを実装
        return []

    def _load_leadership_events(self, year: int) -> List:
        """指定年のリーダーシップイベントを読み込み"""
        # TODO: 完全なタイムラインからフィルタリングするロジックを実装
        return []

    def _load_all_ceo_successions(self) -> List[CeoSuccessionDecision]:
        """全CEO交代履歴を読み込み"""
        # TODO: ceo_succession_service から取得するロジックを実装
        return []

    def _load_all_executive_successions(self) -> List[ExecutiveSuccessionDecision]:
        """全経営チーム交代履歴を読み込み"""
        # TODO: executive_team_succession_service から取得するロジックを実装
        return []

    def _load_all_annual_reports(self) -> List[AnnualReport]:
        """全年次レポートを読み込み"""
        reports = []
        if os.path.exists(self.history_dir):
            for year_dir in os.listdir(self.history_dir):
                year_path = os.path.join(self.history_dir, year_dir)
                if os.path.isdir(year_path):
                    report_path = os.path.join(year_path, 'annual_report.json')
                    if os.path.exists(report_path):
                        try:
                            with open(report_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            reports.append(AnnualReport(**data))
                        except Exception:
                            continue
        return reports