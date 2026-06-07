import json
import math
import os
from typing import Dict, List, Optional

from ..models.executive_narrative_model import (
    AnnualNarrative,
    DecisionRationale,
    ExecutiveNarrative,
    MonthlyNarrative,
    MultiYearNarrative,
    NarrativeSection,
)
from .business_portfolio_service import BusinessPortfolioService
from .company_operations_integration_service import CompanyOperationsIntegrationService
from .corporate_fundamentals_service import CorporateFundamentalsService
from .external_environment_service import ExternalEnvironmentService
from .executive_meeting_service import ExecutiveMeetingService
from .executive_narrative_engine import ExecutiveNarrativeEngine
from .improvement_cycle_service import ImprovementCycleService
from .operational_issues_service import OperationalIssuesService


class ExecutiveNarrativeService:
    def __init__(self, data_path: Optional[str] = None):
        self.integration_service = CompanyOperationsIntegrationService()
        self.fundamentals_service = CorporateFundamentalsService()
        self.environment_service = ExternalEnvironmentService()
        self.portfolio_service = BusinessPortfolioService()
        self.meeting_service = ExecutiveMeetingService()
        self.issues_service = OperationalIssuesService()
        self.improvement_service = ImprovementCycleService()
        self.narrative_engine = ExecutiveNarrativeEngine()
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        ) if data_path is None else data_path
        self.narrative_history_file = os.path.join(self.data_path, 'executive_narratives.json')

    def _load_narrative_history(self) -> List[Dict[str, object]]:
        if not os.path.exists(self.narrative_history_file):
            return []

        with open(self.narrative_history_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_narrative_history(self, narratives: List[Dict[str, object]]) -> None:
        with open(self.narrative_history_file, 'w', encoding='utf-8') as f:
            json.dump(narratives, f, indent=2, ensure_ascii=False)

    def generate_and_store_narrative(
        self,
        period: str,
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        meeting_state: Dict[str, object],
    ) -> ExecutiveNarrative:
        narrative = self.narrative_engine.build_monthly_narrative(
            period=period,
            financials=financials,
            market_state=market_state,
            org_state=org_state,
            meeting_state=meeting_state,
        )
        narratives = self._load_narrative_history()
        existing = [item for item in narratives if item.get('period') == period]
        if existing:
            narratives = [item for item in narratives if item.get('period') != period]
        narratives.append(narrative.model_dump())
        narratives.sort(key=lambda item: item.get('period', ''))
        self._save_narrative_history(narratives)
        return narrative

    def get_narrative(self, period: str) -> ExecutiveNarrative:
        narratives = self._load_narrative_history()
        match = next((item for item in narratives if item.get('period') == period), None)
        if not match:
            raise FileNotFoundError(f'Narrative not found for period: {period}')
        return ExecutiveNarrative(**match)

    def list_narratives(self, limit: int = 6) -> List[ExecutiveNarrative]:
        if limit < 1:
            raise ValueError('limit must be 1 or greater')
        narratives = self._load_narrative_history()
        narratives.sort(key=lambda item: item.get('period', ''))
        return [ExecutiveNarrative(**item) for item in narratives[-limit:]]

    def get_latest_narrative(self) -> ExecutiveNarrative:
        narratives = self._load_narrative_history()
        if not narratives:
            raise FileNotFoundError('No narratives available')
        narratives.sort(key=lambda item: item.get('period', ''))
        return ExecutiveNarrative(**narratives[-1])

    def _get_monthly_inputs(self, month: int) -> Dict[str, object]:
        if month < 1 or month > 12:
            raise ValueError('month must be between 1 and 12')

        monthly_state = self.integration_service.simulate_month_full(month)
        fundamentals = self.fundamentals_service.load_fundamentals()
        environment_state = self.environment_service.build_environment_state(month, 2026)
        portfolio_state = self.portfolio_service.simulate_portfolio_cycle(month)
        meeting_state = self.meeting_service.load_latest_state_for_month(month)
        issue_list = self.issues_service.detect_issues(
            monthly_state,
            monthly_state.get('pl', {}).get('kpis', {}),
            month,
        )
        improvement_state = self.improvement_service.load_cycle_state()
        executed_actions = [action for action in improvement_state.executed_actions if action.month == month]

        return {
            'month': month,
            'monthly_state': monthly_state,
            'fundamentals': fundamentals,
            'environment': environment_state,
            'portfolio_state': portfolio_state,
            'meeting_state': meeting_state,
            'issues': issue_list,
            'improvements': executed_actions,
        }

    def _calculate_sentiment(self, monthly_state: Dict[str, object], issues: List[object]) -> str:
        pl = monthly_state.get('pl', {})
        profit_margin = float(pl.get('profit_margin', 0.0))
        profit = float(pl.get('profit', 0.0))
        revenue = float(sum(pl.get('revenue', {}).values()) if isinstance(pl.get('revenue', {}), dict) else 0.0)
        issue_count = len(issues)
        issue_severity = sum(1 for issue in issues if getattr(issue, 'severity', '') in {'High', 'Critical'})

        score = profit_margin * 3 + (profit / (revenue + 1)) - issue_count * 0.4 + issue_severity * -0.5

        if score > 1.2:
            return 'Positive'
        if score < 0.5:
            return 'Negative'
        return 'Neutral'

    def _build_key_drivers(self, inputs: Dict[str, object]) -> List[str]:
        drivers = []
        environment = inputs['environment']
        fundamentals = inputs['fundamentals']
        portfolio = inputs['portfolio_state']
        meeting = inputs['meeting_state']

        environment_trends = environment.get('trend_effects', {})
        if environment_trends:
            drivers.append('外部環境のトレンド変化が市場機会を左右しました。')
        if environment.get('active_shocks'):
            drivers.append('継続する市場ショックが戦略判断を加速させました。')
        drivers.extend([f"企業の強み: {advantage}" for advantage in fundamentals.profile.competitive_advantages[:2]])
        drivers.append(f"会議での意思決定が経営資源配分に影響しました (決定数 {len(meeting.decisions)})。")

        portfolio_actions = {d.decision for d in portfolio.decisions}
        if 'Invest' in portfolio_actions:
            drivers.append('成長セクターへの投資判断が今月の重心となりました。')
        if 'Exit' in portfolio_actions:
            drivers.append('高リスク事業の撤退判断がリスク低減に寄与しました。')

        return drivers[:5]

    def _build_risks(self, inputs: Dict[str, object]) -> List[str]:
        environment = inputs['environment']
        issues = inputs['issues']
        fundamentals = inputs['fundamentals']
        portfolio = inputs['portfolio_state']

        risks = []
        if environment.get('active_shocks'):
            risks.append('外部ショックによる市場変動リスクが継続しています。')
        if any(issue.severity == 'Critical' for issue in issues):
            risks.append('重要課題の未解決が収益と組織信頼を圧迫しています。')
        if any(d.decision == 'Exit' for d in portfolio.decisions):
            risks.append('撤退判断の実行には組織変革コストが伴います。')
        if fundamentals.financials.cash_reserves < 2.0:
            risks.append('現金余力の縮小が成長投資の制約要因です。')
        if not risks:
            risks.append('現在の経営の最大リスクは変化の速度を見誤ることです。')

        return risks[:4]

    def _build_opportunities(self, inputs: Dict[str, object]) -> List[str]:
        environment = inputs['environment']
        fundamentals = inputs['fundamentals']
        portfolio = inputs['portfolio_state']

        opportunities = []
        market_sizes = environment.get('market_size_by_segment', {})
        high_growth = sorted(market_sizes.items(), key=lambda item: item[1], reverse=True)
        if high_growth:
            opportunities.append(f"成長市場: {high_growth[0][0]}の拡大が新たな収益機会を示唆しています。")
        if any(d.decision == 'NewBusiness' for d in portfolio.decisions):
            opportunities.append('新規事業の可能性が経営の次の成長軸を示しています。')
        if fundamentals.profile.management_style.lower() in {'aggressive', 'balanced'}:
            opportunities.append('企業の経営スタイルが積極的成長に適合しています。')
        if fundamentals.profile.vision:
            opportunities.append('ビジョンに沿った戦略転換がブランド価値を強化します。')

        return opportunities[:4]

    def generate_monthly_narrative(self, month: int) -> MonthlyNarrative:
        inputs = self._get_monthly_inputs(month)
        monthly_state = inputs['monthly_state']
        fundamentals = inputs['fundamentals']
        environment = inputs['environment']
        portfolio = inputs['portfolio_state']
        meeting = inputs['meeting_state']
        issues = inputs['issues']
        improvements = inputs['improvements']

        sentiment = self._calculate_sentiment(monthly_state, issues)
        key_drivers = self._build_key_drivers(inputs)
        risks = self._build_risks(inputs)
        opportunities = self._build_opportunities(inputs)

        pl = monthly_state.get('pl', {})
        revenue = sum(pl.get('revenue', {}).values()) if isinstance(pl.get('revenue', {}), dict) else 0.0
        profit_margin = float(pl.get('profit_margin', 0.0))
        issue_count = len(issues)
        approved = sum(1 for decision in meeting.decisions if decision.decision == 'Approve')

        sections = [
            NarrativeSection(
                id='context',
                title='外部環境と企業の立ち位置',
                content=(
                    f"{fundamentals.profile.name}は今月、市場環境の変化と自社の強みを改めて照らし合わせました。"
                    f"外部環境では{len(environment.get('active_shocks', []))}件のショックが確認され、トレンド変化が{len(environment.get('trend_effects', {}))}件の機会と脅威を同時に作り出しています。"
                ),
                highlights=[
                    f"市場規模が拡大しているセグメント: {next(iter(environment.get('market_size_by_segment', {}).keys()), 'N/A')}。",
                    f"企業の強みは{fundamentals.profile.competitive_advantages[:2]}に集中しています。",
                ],
            ),
            NarrativeSection(
                id='response',
                title='課題認識と経営判断',
                content=(
                    f"内部では、{issue_count}件の経営課題が浮かび上がり、改善アクションとポートフォリオ意思決定が同時に進みました。"
                    f"経営会議では{approved}件の承認決定が得られ、資本配分と業務改善の接続を図りました。"
                ),
                highlights=[
                    f"会議で承認された意思決定数: {approved}",
                    f"改善アクション数: {len(improvements)}", 
                ],
            ),
            NarrativeSection(
                id='outcome',
                title='結果と見通し',
                content=(
                    f"売上{revenue:.3f}、利益率{profit_margin:.3f}の結果から、経営は自社の資本と機会のバランスを再確認しました。"
                    f"投資・撤退判断は今後の事業ポートフォリオの変化を予兆しています。"
                ),
                highlights=[
                    f"今月の主な投資判断: {', '.join({d.decision for d in portfolio.decisions}) or 'なし'}。",
                    f"リスクと機会の両面から次月の見直しを進めます。",
                ],
            ),
        ]

        return MonthlyNarrative(
            month=month,
            sections=sections,
            sentiment=sentiment,
            key_drivers=key_drivers,
            risks=risks,
            opportunities=opportunities,
        )

    def generate_annual_narrative(self, year: int) -> AnnualNarrative:
        if year < 2020 or year > 2030:
            raise ValueError('year must be between 2020 and 2030')

        monthly_narratives = [self.generate_monthly_narrative(month) for month in range(1, 13)]
        fundamentals = self.fundamentals_service.load_fundamentals()

        sentiment_counts = {label: 0 for label in ['Positive', 'Neutral', 'Negative']}
        for monthly in monthly_narratives:
            sentiment_counts[monthly.sentiment] += 1

        major_events = [
            f"{month.month}月: {', '.join(month.key_drivers[:2]) if month.key_drivers else '経営の焦点が明確化'}"
            for month in monthly_narratives
        ][:5]

        business_unit_stories = {
            unit.name: (
                f"{unit.name}は市場と企業の強みを掛け合わせ、{unit.risk_factors[:2]}を踏まえて成長を試みました。"
            )
            for unit in fundamentals.business_units[:3]
        }

        strategic_shift = (
            "年間を通じて、企業は外部環境の変化を受け止めつつ、"
            "成長ポートフォリオへの投資と高リスク事業の資本再配分を進めました。"
        )

        outlook_next_year = (
            "来年は戦略的な重点領域をさらに明確にし、デジタルとライセンス事業の競争優位を活かしながら、"
            "リスク管理と実行力を両立させる必要があります。"
        )

        return AnnualNarrative(
            year=year,
            summary=(
                f"{year}年の経営は、外部環境の変化と内部改善の両輪で進展しました。"
                f"12ヶ月を通じて得られた知見は、企業文化と戦略の整合性を高めることに貢献しました。"
            ),
            major_events=major_events,
            business_unit_stories=business_unit_stories,
            strategic_shift=strategic_shift,
            outlook_next_year=outlook_next_year,
        )

    def generate_multi_year_narrative(self, start_year: int, end_year: int) -> MultiYearNarrative:
        if start_year < 2000 or end_year < start_year:
            raise ValueError('invalid year range for multi-year narrative')

        fundamentals = self.fundamentals_service.load_fundamentals()
        history = [event for event in fundamentals.history if start_year <= event.year <= end_year]

        transformation_story = (
            f"{start_year}年から{end_year}年にかけて、企業は自らの強みを再定義し、"
            "外部市場の変化を受け止めながら構造的な成長基盤を築きました。"
        )

        growth_drivers = [
            f"競争優位性: {fundamentals.profile.competitive_advantages[0]}",
            '市場トレンドへの適応力',
            '戦略的資本配分とポートフォリオ再編成',
        ]

        structural_changes = [
            '事業ポートフォリオの再編成',
            '改善サイクルの定着と意思決定の高速化',
            '組織文化の強みを軸にした運営改革',
        ]

        if history:
            structural_changes.append(f"過去の重要イベント: {history[0].title}")
            transformation_story += f" 特に{history[0].title}はその転機でした。"

        long_term_outlook = (
            "今後は、企業の核となる強みを軸にしつつ、"
            "市場機会とリスクをバランスさせた持続的成長を描くことが鍵となります。"
        )

        return MultiYearNarrative(
            start_year=start_year,
            end_year=end_year,
            transformation_story=transformation_story,
            growth_drivers=growth_drivers,
            structural_changes=structural_changes[:4],
            long_term_outlook=long_term_outlook,
        )
