from typing import Dict, List, Optional

from ..models.executive_narrative_model import DecisionRationale, ExecutiveNarrative


class ExecutiveNarrativeEngine:
    def build_monthly_narrative(
        self,
        period: str,
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        meeting_state: Dict[str, object],
    ) -> ExecutiveNarrative:
        summary = self._build_summary(period, financials, market_state, org_state, meeting_state)
        financial_section = self._build_financial_section(financials)
        market_section = self._build_market_section(market_state)
        organization_section = self._build_org_section(org_state)
        investment_section = self._build_investment_section(financials, meeting_state)
        risk_section = self._build_risk_section(financials, market_state, org_state, meeting_state)
        decisions_section = self._build_decisions_section(meeting_state)
        next_month_focus = self._build_next_month_focus(financials, market_state, org_state, meeting_state)
        ceo_persona = self._build_ceo_persona(meeting_state)
        decision_commentary = self._build_decision_commentary(meeting_state)

        return ExecutiveNarrative(
            period=period,
            summary=summary,
            financial_section=financial_section,
            market_section=market_section,
            organization_section=organization_section,
            investment_section=investment_section,
            risk_section=risk_section,
            decisions_section=decisions_section,
            next_month_focus=next_month_focus,
            ceo_persona=ceo_persona,
            decision_commentary=decision_commentary,
        )

    def _build_summary(
        self,
        period: str,
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        meeting_state: Dict[str, object],
    ) -> str:
        cash = float(financials.get('cash_balance', 0.0))
        profit_margin = float(financials.get('profit_margin', 0.0))
        selected_option = meeting_state.get('selected_option_id') or 'N/A'
        agenda_count = len(meeting_state.get('agenda', []))

        return (
            f"{period}は、月次の数値と経営会議での議論を踏まえた意思決定が重視された月でした。"
            f"会議では{agenda_count}件の議題を議論し、最終的に「{selected_option}」の方針が選択されました。"
            f"現金残高は{cash:.3f}、利益率は{profit_margin:.3f}であり、資本効率と組織の実行力を両立させる必要があります。"
        )

    def _build_financial_section(self, financials: Dict[str, object]) -> str:
        cash = float(financials.get('cash_balance', 0.0))
        profit = float(financials.get('profit', 0.0))
        revenue = float(sum(financials.get('revenue', {}).values()) if isinstance(financials.get('revenue'), dict) else financials.get('revenue', 0.0))
        debt = float(financials.get('short_term_debt', 0.0) + financials.get('long_term_debt', 0.0))
        liquidity = float(financials.get('available_credit_line', 0.0))

        return (
            f"財務面では、売上{revenue:.3f}、利益{profit:.3f}、現金残高{cash:.3f}を記録しました。"
            f"負債合計は{debt:.3f}で、利用可能な与信枠は{liquidity:.3f}です。"
            "このバランスは投資余力と流動性の両立を求めています。"
        )

    def _build_market_section(self, market_state: Dict[str, object]) -> str:
        segments = market_state.get('market_index_by_segment', {})
        active_shocks = market_state.get('active_events', [])
        top_segment = next(iter(segments.keys()), '市場全体') if segments else '市場全体'
        shock_count = len(active_shocks)

        return (
            f"市場では、特に{top_segment}が注目される領域になっています。"
            f"現在アクティブな市場イベントは{shock_count}件で、外部環境の変化が依然として経営判断の重要な材料です。"
            "競合と顧客動向の両面を引き続き注視する必要があります。"
        )

    def _build_org_section(self, org_state: Dict[str, object]) -> str:
        units = org_state.get('units', [])
        total_headcount = sum(unit.get('headcount', 0) for unit in units if isinstance(unit, dict))
        avg_workload = 0.0
        if units:
            avg_workload = sum(unit.get('workload_index', 0.0) for unit in units if isinstance(unit, dict)) / len(units)

        return (
            f"組織面では、総人員は{total_headcount}名で、平均稼働率は{avg_workload:.3f}です。"
            "高負荷部門への負担分散と人材定着の両面を意識した施策が必要です。"
        )

    def _build_investment_section(
        self,
        financials: Dict[str, object],
        meeting_state: Dict[str, object],
    ) -> str:
        options = meeting_state.get('decision_options', [])
        selected_id = meeting_state.get('selected_option_id')
        selected = next((opt for opt in options if opt.get('id') == selected_id), None)
        selected_label = selected.get('label') if isinstance(selected, dict) else '選択なし'

        return (
            f"投資判断では、{selected_label}が選ばれました。"
            "この方針はキャッシュと実行力のバランスを意識したものです。"
        )

    def _build_risk_section(
        self,
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        meeting_state: Dict[str, object],
    ) -> str:
        risks = []
        if float(financials.get('cash_balance', 0.0)) < float(financials.get('minimum_cash_threshold', 0.0,)) if isinstance(financials.get('minimum_cash_threshold', None), (int, float)) else False:
            risks.append('流動性リスクが高まっています。')
        if market_state.get('active_events'):
            risks.append('市場ショックが継続し、収益見通しが不透明です。')
        if any(unit.get('workload_index', 0.0) > 1.1 for unit in org_state.get('units', []) if isinstance(unit, dict)):
            risks.append('組織の実行力が一部で逼迫しています。')
        if not risks:
            risks.append('特段の大きなリスクは見られませんが、変化速度には注意が必要です。')

        return ' '.join(risks)

    def _build_decisions_section(self, meeting_state: Dict[str, object]) -> DecisionRationale:
        selected_id = meeting_state.get('selected_option_id') or 'N/A'
        options = meeting_state.get('decision_options', [])
        selected = next((opt for opt in options if opt.get('id') == selected_id), None)
        board = meeting_state.get('board_decision', {}) if isinstance(meeting_state.get('board_decision'), dict) else None
        final_actor = meeting_state.get('decision_actor') or ('AI CEO' if meeting_state.get('ceo_selected_option_label') else 'User')
        final_option = (
            board.get('final_option_label') if board and board.get('final_option_label')
            else meeting_state.get('ceo_selected_option_label')
            or (selected.get('label') if isinstance(selected, dict) else '選択案')
        )
        final_rationale = meeting_state.get('ceo_decision_rationale') or ''

        if selected is None:
            return DecisionRationale(
                option_id=selected_id,
                label='未選択',
                pros=[],
                cons=[],
                why_chosen='現時点で決定案が選択されていません。',
                final_decision_actor=final_actor,
                final_decision_option=final_option,
                final_decision_rationale=final_rationale or '最終決定の詳細は利用できません。',
                board_status=board.get('status') if board else None,
                board_final_option=board.get('final_option_label') if board else None,
                board_rationale=board.get('board_rationale') if board else None,
                board_conditions=board.get('conditions') if board else None,
                board_member_opinions=board.get('member_opinions', []) if board else [],
            )

        label = selected.get('label', '選択案')
        pros = selected.get('pros', []) if isinstance(selected.get('pros', []), list) else []
        cons = selected.get('cons', []) if isinstance(selected.get('cons', []), list) else []
        why = (
            f"{final_actor}は{final_option}を選択しました。"
            f"理由は、{final_rationale if final_rationale else ('、'.join(pros[:2]) if pros else '経済合理性とリスク管理のバランスを重視したため')}。")

        return DecisionRationale(
            option_id=selected_id,
            label=label,
            pros=pros,
            cons=cons,
            why_chosen=why,
            final_decision_actor=final_actor,
            final_decision_option=final_option,
            final_decision_rationale=final_rationale,
            board_status=board.get('status') if board else None,
            board_final_option=board.get('final_option_label') if board else None,
            board_rationale=board.get('board_rationale') if board else None,
            board_conditions=board.get('conditions') if board else None,
            board_member_opinions=board.get('member_opinions', []) if board else [],
        )

    def _build_next_month_focus(
        self,
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        meeting_state: Dict[str, object],
    ) -> List[str]:
        focus = []
        if meeting_state.get('selected_option_id') == 'A':
            focus.append('投資継続の収益効果を定期的に確認する。')
            focus.append('実行負荷の増大に対する対応策を整備する。')
        elif meeting_state.get('selected_option_id') == 'B':
            focus.append('流動性の改善状況を確認し、余力を可視化する。')
            focus.append('成長機会の再評価を行う。')
        else:
            focus.append('選択したバランス案の実行進捗を週次で追跡する。')
            focus.append('コストと投資の両面を定点観測する。')

        if float(financials.get('cash_balance', 0.0)) < 2.0:
            focus.append('現金残高の確保を最優先課題とする。')
        if market_state.get('active_events'):
            focus.append('市場ショックの影響を逐次確認する。')

        if not focus:
            focus.append('経営判断の実行状況を継続的に評価する。')

        return focus[:5]

    def _build_ceo_persona(self, meeting_state: Dict[str, object]) -> Optional[Dict[str, float]]:
        if isinstance(meeting_state.get('ceo_persona'), dict):
            return {
                key: float(value)
                for key, value in meeting_state['ceo_persona'].items()
                if isinstance(value, (int, float))
            }
        return None

    def _build_decision_commentary(self, meeting_state: Dict[str, object]) -> str:
        persona = meeting_state.get('ceo_persona')
        rationale = meeting_state.get('ceo_decision_rationale', '')
        board = meeting_state.get('board_decision', {}) if isinstance(meeting_state.get('board_decision'), dict) else None
        member_opinions = board.get('member_opinions', []) if board else []

        commentary = rationale or '最終判断は経営戦略と顧客・市場環境を勘案して行われました。'

        if member_opinions:
            board_insights = []
            for op in member_opinions:
                role = op.get('member_role', '取締役')
                pref = op.get('preferred_option_id', '')
                risk = 'リスク指摘あり' if op.get('risk_flag') else 'リスクなし'
                board_insights.append(f"{role}: {pref}推奨 ({risk})")
            commentary += f" 取締役会では以下の意見が出されました: {'; '.join(board_insights)}。"

        if persona:
            commentary = (
                '2026年のホリプロの興行・ライブ・IP強化戦略に沿い、'
                f'攻めと回転率、ブランド価値のバランスを重視した最終判断です。{commentary}'
            )

        return commentary
