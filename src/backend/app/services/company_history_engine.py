import os
from typing import List, Dict, Optional
from datetime import datetime
from ..models.company_history_model import LeadershipEvent, AnnualReport, CompanyHistory
from ..models.ceo_succession_model import CeoSuccessionDecision
from ..models.executive_team_succession_model import ExecutiveSuccessionDecision
from ..models.culture_model import CultureProfile
from ..models.external_environment_model_v2 import ExternalEnvironmentState
from ..models.enterprise_evolution_model import EnterpriseEvolutionResult
from .monthly_batch_service import MonthlyBatchResult


class CompanyHistoryEngine:
    """企業の歴史生成エンジン"""

    def build_leadership_timeline(
        self,
        ceo_succession_history: List[CeoSuccessionDecision],
        executive_succession_history: List[ExecutiveSuccessionDecision],
    ) -> List[LeadershipEvent]:
        """CEOと経営チームの交代履歴からタイムラインを構築"""
        events = []

        # CEO交代イベント
        for succession in ceo_succession_history:
            event = LeadershipEvent(
                period=succession.period,
                event_type="ceo_succession",
                role="CEO",
                from_name=succession.outgoing_ceo_name if hasattr(succession, 'outgoing_ceo_name') else None,
                to_name=succession.selected_candidate_name if hasattr(succession, 'selected_candidate_name') else None,
                rationale=succession.rationale if hasattr(succession, 'rationale') else None
            )
            events.append(event)

        # 経営チーム交代イベント
        for succession in executive_succession_history:
            event = LeadershipEvent(
                period=succession.period,
                event_type="executive_succession",
                role=succession.role_id,  # 仮定: role_id をロール名として使用
                from_name=None,  # モデルにないのでNone
                to_name=None,    # モデルにないのでNone
                rationale=succession.rationale
            )
            events.append(event)

        # 時系列でソート
        events.sort(key=lambda x: x.period)
        return events

    def build_annual_report(
        self,
        year: int,
        monthly_results: List[MonthlyBatchResult],
        culture_history: List[CultureProfile],
        evolution_history: List[EnterpriseEvolutionResult],
        environment_history: List[ExternalEnvironmentState],
        leadership_events: List[LeadershipEvent],
    ) -> AnnualReport:
        """
        年次レポートを構築
        - 年間売上・利益集計
        - その年の主要イベント
        - 文化トレンド（前年→今年の差分）
        - evolution_score の年間平均 or 変化量
        - Markdown レポート本文を生成
        """
        # 年間財務集計
        revenue_total = sum(result.pl.get('total_revenue', 0) for result in monthly_results if result.pl)
        profit_total = sum(result.pl.get('operating_profit', 0) for result in monthly_results if result.pl)

        # 主要イベント抽出（対象年のリーダーシップイベント + 大きなショック）
        major_events = []
        year_str = str(year)

        # リーダーシップイベント
        for event in leadership_events:
            if event.period.startswith(year_str):
                if event.event_type == "ceo_succession":
                    major_events.append(f"CEO交代: {event.from_name or '不明'} → {event.to_name or '不明'}")
                elif event.event_type == "executive_succession":
                    major_events.append(f"{event.role}交代: {event.from_name or '不明'} → {event.to_name or '不明'}")

        # 外部環境ショック
        for env in environment_history:
            if env.period.startswith(year_str) and env.shocks:
                for shock in env.shocks:
                    if shock.severity == "critical":
                        major_events.append(f"重大ショック: {shock.description}")

        # 文化トレンド（前年との比較 - 簡易版）
        culture_trends = {}
        if culture_history:
            current_year_cultures = [c for c in culture_history if c.period.startswith(year_str)]
            prev_year_cultures = [c for c in culture_history if c.period.startswith(str(year-1))]

            if current_year_cultures and prev_year_cultures:
                current_avg = self._average_culture(current_year_cultures[-1])
                prev_avg = self._average_culture(prev_year_cultures[-1])

                for key in current_avg:
                    culture_trends[key] = current_avg[key] - prev_avg[key]

        # 進化トレンド（年間平均）
        evolution_scores = [e.evolution_score for e in evolution_history if e.period.startswith(year_str)]
        evolution_trend = sum(evolution_scores) / len(evolution_scores) if evolution_scores else 0.0

        # Markdown生成
        markdown_content = self.render_annual_report_markdown(
            year, revenue_total, profit_total, major_events, culture_trends, evolution_trend
        )

        # Markdownファイル保存
        reports_dir = os.path.join(os.path.dirname(__file__), '../../../data/reports/annual')
        os.makedirs(reports_dir, exist_ok=True)
        markdown_path = os.path.join(reports_dir, f'{year}.md')

        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return AnnualReport(
            year=year,
            revenue_total=revenue_total,
            profit_total=profit_total,
            major_events=major_events,
            culture_trends=culture_trends,
            evolution_trend=evolution_trend,
            summary_markdown_path=markdown_path
        )

    def render_annual_report_markdown(
        self,
        year: int,
        revenue_total: float,
        profit_total: float,
        major_events: List[str],
        culture_trends: Dict[str, float],
        evolution_trend: float
    ) -> str:
        """年次レポートのMarkdownを生成"""
        return f"""# 年次レポート {year}

## 1. 財務サマリ
- 売上合計: ¥{revenue_total:,.0f}
- 営業利益: ¥{profit_total:,.0f}

## 2. 主要イベント
{chr(10).join(f"- {e}" for e in major_events) if major_events else "- 特記事項なし"}

## 3. 文化トレンド
{chr(10).join(f"- {k}: {v:+.2f}" for k, v in culture_trends.items()) if culture_trends else "- データなし"}

## 4. 進化スコア
- 年間進化トレンド: {evolution_trend:+.3f}

---
*生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _average_culture(self, culture: CultureProfile) -> Dict[str, float]:
        """文化プロファイルの平均値を計算"""
        return {
            'aggressiveness': culture.aggressiveness_culture,
            'risk_aversion': culture.risk_aversion_culture,
            'brand': culture.brand_culture,
            'cost': culture.cost_culture,
            'people': culture.people_culture,
            'execution': culture.execution_culture,
            'innovation': culture.innovation_culture,
            'stability': culture.stability_culture,
        }