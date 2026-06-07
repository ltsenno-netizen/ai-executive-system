from typing import Dict, List

from ..models.executive_report_model import ExecutiveReport, ReportSection
from ..models.executive_narrative_model import ExecutiveNarrative


class ExecutiveReportEngine:
    def build_monthly_report(
        self,
        period: str,
        narrative: ExecutiveNarrative,
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        meeting_state: Dict[str, object],
    ) -> ExecutiveReport:
        title = self._build_title(period)

        sections = [
            ReportSection(
                title='2. 財務ハイライト',
                body=self._build_financial_highlights(financials),
                order=1,
            ),
            ReportSection(
                title='3. 市場・顧客',
                body=self._build_market_customer_section(market_state),
                order=2,
            ),
            ReportSection(
                title='4. 組織・実行力',
                body=self._build_organization_execution_section(org_state, meeting_state),
                order=3,
            ),
            ReportSection(
                title='5. 取締役会の判断',
                body=self._build_board_review_section(meeting_state),
                order=4,
            ),
            ReportSection(
                title='6. CEO 経営スタイル（2026）',
                body=self._build_ceo_persona_section(meeting_state),
                order=5,
            ),
            ReportSection(
                title='7. 投資・トランシェ',
                body=self._build_investment_tranche_section(narrative, meeting_state),
                order=6,
            ),
            ReportSection(
                title='8. リスクと注目ポイント',
                body=self._build_risks_and_watchpoints(narrative, market_state, org_state),
                order=7,
            ),
            ReportSection(
                title='9. 今後のフォーカス',
                body=self._build_next_month_focus(narrative),
                order=8,
            ),
        ]


        return ExecutiveReport(
            period=period,
            title=title,
            management_summary=narrative.summary,
            sections=sections,
        )

    def render_report_markdown(self, report: ExecutiveReport) -> str:
        lines = [
            f"# 月次経営レポート — {self._format_report_label(report.period)}",
            "",
            "## 1. マネジメントサマリ",
            report.management_summary,
            "",
        ]

        for section in sorted(report.sections, key=lambda item: item.order):
            lines.extend([
                f"## {section.title}",
                section.body,
                "",
            ])

        return "\n".join(lines).strip() + "\n"

    def _build_title(self, period: str) -> str:
        return f"月次経営レポート {self._format_report_label(period)}"

    def _format_report_label(self, period: str) -> str:
        year, month = period.split('-')
        return f"{year}年{int(month)}月"

    def _to_bullet_list(self, items: List[str]) -> str:
        return "\n".join(f"- {item}" for item in items if item)

    def _build_financial_highlights(self, financials: Dict[str, object]) -> str:
        revenue = float(sum(financials.get('revenue', {}).values()) if isinstance(financials.get('revenue'), dict) else financials.get('revenue', 0.0))
        profit = float(financials.get('profit', 0.0))
        cash = float(financials.get('cash_balance', 0.0))
        profit_margin = float(financials.get('profit_margin', 0.0))
        invest_requests = financials.get('investment_requests_pending', [])

        highlights = [
            f"売上: {revenue:.3f}",
            f"営業利益: {profit:.3f}",
            f"キャッシュ残高: {cash:.3f}",
            f"利益率: {profit_margin:.3f}",
            f"投資リクエスト保留数: {len(invest_requests)}",
        ]
        return self._to_bullet_list(highlights)

    def _build_market_customer_section(self, market_state: Dict[str, object]) -> str:
        segments = market_state.get('market_index_by_segment', {})
        top_segment = next(iter(segments.keys()), '市場全体')
        active_events = market_state.get('active_events', [])
        event_summary = f"アクティブな市場イベント数: {len(active_events)}。" if active_events else "現在、特段の市場イベントは発生していません。"

        return (
            f"主要セグメントは{top_segment}です。{event_summary}"
            "外部環境の変化と顧客動向を連動させた戦略の実行が求められます。"
        )

    def _build_board_review_section(self, meeting_state: Dict[str, object]) -> str:
        board = meeting_state.get('board_decision') if isinstance(meeting_state.get('board_decision'), dict) else None
        if not board:
            return '取締役会による最終レビュー情報は利用できません。'

        lines = [
            f"CEO 提案: {meeting_state.get('ceo_selected_option_label', '不明')}",
            f"Board 判定: {board.get('status', '不明')}",
            f"最終決定案: {board.get('final_option_label', '不明')}",
            f"理由: {board.get('board_rationale', '説明なし')}",
        ]
        if board.get('conditions'):
            lines.append(f"条件: {board.get('conditions')}")

        member_opinions = board.get('member_opinions', [])
        if member_opinions:
            lines.append("取締役意見:")
            for op in member_opinions:
                role = op.get('member_role', '取締役')
                pref = op.get('preferred_option_id', '')
                rationale = op.get('rationale', '')
                risk = ' (リスク指摘)' if op.get('risk_flag') else ''
                lines.append(f"  - {role}: {pref}推奨{risk} - {rationale}")

        return '\n'.join(lines)

    def _build_organization_execution_section(self, org_state: Dict[str, object], meeting_state: Dict[str, object]) -> str:
        units = org_state.get('units', [])
        total_headcount = sum(unit.get('headcount', 0) for unit in units if isinstance(unit, dict))
        open_positions = sum(1 for unit in units if isinstance(unit, dict) and unit.get('open_positions', 0) > 0)
        selected_option = meeting_state.get('selected_option_id', 'N/A')

        return (
            f"組織の総人員は{total_headcount}名、残存オープンポジションは{open_positions}件です。"
            f"経営会議では{selected_option}を中心に意思決定が行われ、実行力の強化がテーマになりました。"
        )

    def _build_investment_tranche_section(self, narrative: ExecutiveNarrative, meeting_state: Dict[str, object]) -> str:
        selected_option = meeting_state.get('selected_option_id', 'N/A')
        selected_label = meeting_state.get('ceo_selected_option_label') or meeting_state.get('decision_options', [{}])[0].get('label', '選択案')
        decision_actor = meeting_state.get('decision_actor') or 'User'
        rationale = meeting_state.get('ceo_decision_rationale', '')
        content = narrative.investment_section or ''

        decision_summary = (
            f"最終決定:\n- 決定者: {decision_actor}\n- 選択案: {selected_label}"
        )
        if rationale:
            decision_summary += f"\n- 理由: {rationale}"

        return (
            f"{content}\n\n" if content else ""
        ) + f"決定された投資姿勢は{selected_option}です。\n\n{decision_summary}"

    def _build_ceo_persona_section(self, meeting_state: Dict[str, object]) -> str:
        persona = meeting_state.get('ceo_persona') or {}
        if not isinstance(persona, dict) or not persona:
            return 'AI CEOの経営スタイル情報は現時点で利用できません。'

        lines = [
            'AI CEOの経営スタイル(2026):',
            f"- 攻め度: {'高い' if persona.get('aggressiveness', 0) >= 0.7 else '中程度' if persona.get('aggressiveness', 0) >= 0.4 else '低い'}",
            f"- リスク許容度: {'中程度' if 0.4 <= persona.get('risk_tolerance', 0) < 0.8 else '高い' if persona.get('risk_tolerance', 0) >= 0.8 else '低い'}",
            f"- ブランド重視: {'高い' if persona.get('brand_priority', 0) >= 0.7 else '中程度' if persona.get('brand_priority', 0) >= 0.4 else '低い'}",
            f"- 短期収益: {'中程度' if 0.4 <= persona.get('short_term_focus', 0) < 0.8 else '高い' if persona.get('short_term_focus', 0) >= 0.8 else '低い'}",
            f"- 中期戦略: {'高い' if persona.get('long_term_focus', 0) >= 0.7 else '中程度' if persona.get('long_term_focus', 0) >= 0.4 else '低い'}",
        ]
        if meeting_state.get('ceo_decision_rationale'):
            lines.append('このスタイルに基づき、今月の最終判断は次の理由で選択されました:')
            lines.append(f"- {meeting_state.get('ceo_decision_rationale')}")
        return '\n'.join(lines)

    def _build_risks_and_watchpoints(self, narrative: ExecutiveNarrative, market_state: Dict[str, object], org_state: Dict[str, object]) -> str:
        market_risk = '市場イベントの影響を継続観察する必要があります。' if market_state.get('active_events') else '市場環境は相対的に安定しています。'
        org_risk = '組織の稼働負荷と人材確保を同時に管理する必要があります。' if any(unit.get('workload_index', 0.0) > 1.1 for unit in org_state.get('units', []) if isinstance(unit, dict)) else '組織の実行力は概ね安定しています。'

        return '\n'.join([narrative.risk_section, market_risk, org_risk]).strip()

    def _build_next_month_focus(self, narrative: ExecutiveNarrative) -> str:
        if narrative.next_month_focus:
            return self._to_bullet_list(narrative.next_month_focus)
        return '今後のフォーカス情報は現時点で利用できません。'
