from typing import List, Dict, Any
from ..models.quarterly_review_model import (
    QuarterlyReview,
    QuarterlyFinancialSummary,
    QuarterlyExecutionSummary,
    QuarterlyBoardReview,
)
from ..models.mid_term_plan_model import MidTermPlan
from ..models.ai_ceo_model import AICeoPersona
from ..services.ai_board_members import BaseBoardMember


class QuarterlyReviewEngine:
    def build_quarterly_review(
        self,
        quarter: str,
        monthly_results: List[Dict[str, Any]],
        mid_term_plan: MidTermPlan,
        ceo_persona: AICeoPersona,
        board_members: List[BaseBoardMember]
    ) -> QuarterlyReview:
        # 財務集計（3ヶ月分）
        financial = self._build_financial_summary(quarter, monthly_results, mid_term_plan)

        # 実行サマリ
        execution = self._build_execution_summary(monthly_results)

        # ギャップ分析
        gap_analysis = self._build_gap_analysis(financial, execution, mid_term_plan)

        # 次四半期の重点テーマ生成
        next_quarter_focus = self._generate_next_quarter_focus(gap_analysis, ceo_persona)

        # Board による四半期レビュー（合議制）
        board_review = self._conduct_board_review(
            quarter, financial, execution, gap_analysis, board_members
        )

        return QuarterlyReview(
            quarter=quarter,
            financial=financial,
            execution=execution,
            gap_analysis=gap_analysis,
            next_quarter_focus=next_quarter_focus,
            board_review=board_review,
        )

    def _build_financial_summary(
        self,
        quarter: str,
        monthly_results: List[MonthlyBatchResult],
        mid_term_plan: MidTermPlan
    ) -> QuarterlyFinancialSummary:
        # 3ヶ月分の財務データを集計
        revenue_total = sum(result.financials.get('revenue', 0.0) for result in monthly_results)
        operating_profit_total = sum(result.financials.get('operating_profit', 0.0) for result in monthly_results)
        cash_end = monthly_results[-1].financials.get('cash_balance', 0.0) if monthly_results else 0.0

        # 計画比の計算（簡易版）
        planned_revenue = mid_term_plan.quarterly_targets.get(quarter, {}).get('revenue', revenue_total)
        planned_profit = mid_term_plan.quarterly_targets.get(quarter, {}).get('profit', operating_profit_total)

        revenue_vs_plan = (revenue_total - planned_revenue) / planned_revenue if planned_revenue > 0 else 0.0
        profit_vs_plan = (operating_profit_total - planned_profit) / planned_profit if planned_profit > 0 else 0.0

        return QuarterlyFinancialSummary(
            quarter=quarter,
            revenue_total=revenue_total,
            operating_profit_total=operating_profit_total,
            cash_end=cash_end,
            revenue_vs_plan=revenue_vs_plan,
            profit_vs_plan=profit_vs_plan,
        )

    def _build_execution_summary(self, monthly_results: List[MonthlyBatchResult]) -> QuarterlyExecutionSummary:
        # 実行データの集計
        initiatives_completed = sum(
            len(result.execution.get('completed_initiatives', [])) for result in monthly_results
        )
        initiatives_delayed = sum(
            len(result.execution.get('delayed_initiatives', [])) for result in monthly_results
        )

        # 組織負荷指数の平均
        org_load_indices = [
            result.org_state.get('avg_workload_index', 0.0) for result in monthly_results
        ]
        org_load_index = sum(org_load_indices) / len(org_load_indices) if org_load_indices else 0.0

        return QuarterlyExecutionSummary(
            initiatives_completed=initiatives_completed,
            initiatives_delayed=initiatives_delayed,
            org_load_index=org_load_index,
        )

    def _build_gap_analysis(
        self,
        financial: QuarterlyFinancialSummary,
        execution: QuarterlyExecutionSummary,
        mid_term_plan: MidTermPlan
    ) -> str:
        analysis_parts = []

        # 財務ギャップ
        if financial.revenue_vs_plan > 0.05:
            analysis_parts.append(f"売上は計画を{financial.revenue_vs_plan:.1%}上回り、好調。")
        elif financial.revenue_vs_plan < -0.05:
            analysis_parts.append(f"売上は計画を{abs(financial.revenue_vs_plan):.1%}下回り、改善が必要。")

        if financial.profit_vs_plan < -0.05:
            analysis_parts.append(f"利益は計画を{abs(financial.profit_vs_plan):.1%}下回り、コスト管理の強化を。")

        # 実行ギャップ
        if execution.org_load_index > 0.8:
            analysis_parts.append("組織負荷が高く、持続可能性に懸念。")
        if execution.initiatives_delayed > execution.initiatives_completed * 0.3:
            analysis_parts.append("遅延施策が目立ち、実行力の向上が必要。")

        return " ".join(analysis_parts) if analysis_parts else "大きなギャップは見られず、計画通りの進捗。"

    def _generate_next_quarter_focus(
        self, gap_analysis: str, ceo_persona: AICeoPersona
    ) -> List[str]:
        focus = []

        if "売上" in gap_analysis and "下回り" in gap_analysis:
            focus.append("売上向上施策の強化")
        if "利益" in gap_analysis and "下回り" in gap_analysis:
            focus.append("コスト最適化と利益率改善")
        if "組織負荷" in gap_analysis:
            focus.append("組織負荷の平準化と人材育成")
        if "実行力" in gap_analysis:
            focus.append("プロジェクト管理の改善")

        # CEOの特性を反映
        if ceo_persona.aggressiveness > 0.7:
            focus.append("成長投資機会の積極的評価")
        if ceo_persona.brand_priority > 0.7:
            focus.append("ブランド価値向上施策の推進")

        return focus[:4]  # 最大4つに制限

    def _conduct_board_review(
        self,
        quarter: str,
        financial: QuarterlyFinancialSummary,
        execution: QuarterlyExecutionSummary,
        gap_analysis: str,
        board_members: List[BaseBoardMember]
    ) -> QuarterlyBoardReview:
        # Boardメンバーの評価を集約
        opinions = []
        risk_flags = 0

        for member in board_members:
            # 簡易的な評価（実際にはより詳細なロジックが必要）
            if member.role == "financial":
                risk_flag = financial.profit_vs_plan < -0.1 or financial.cash_end < 1.0
                preferred_status = "conditional" if risk_flag else "approved"
                rationale = f"財務状況を{f'改善' if risk_flag else '維持'}する必要あり。"
            elif member.role == "risk":
                risk_flag = execution.org_load_index > 0.8 or financial.profit_vs_plan < -0.15
                preferred_status = "rejected" if risk_flag else "approved"
                rationale = f"リスク{f'高' if risk_flag else '低'}水準。"
            elif member.role == "brand":
                risk_flag = financial.revenue_vs_plan < -0.1
                preferred_status = "conditional" if risk_flag else "approved"
                rationale = f"ブランド価値への{f'影響' if risk_flag else '貢献'}を考慮。"
            elif member.role == "org":
                risk_flag = execution.org_load_index > 0.9
                preferred_status = "conditional" if risk_flag else "approved"
                rationale = f"組織キャパシティ{f'逼迫' if risk_flag else '適正'}。"
            else:
                risk_flag = False
                preferred_status = "approved"
                rationale = "問題なし。"

            if risk_flag:
                risk_flags += 1

            from ..models.board_member_model import BoardMemberOpinion
            opinions.append(BoardMemberOpinion(
                member_role=member.role,
                preferred_option_id=preferred_status,
                rationale=rationale,
                risk_flag=risk_flag,
            ))

        # 合議制での最終判定
        if risk_flags >= 2:
            status = "rejected"
            rationale = "複数の取締役から重大な懸念が指摘されたため、是正を求める。"
            conditions = "次四半期での改善計画の提出を義務化"
        elif risk_flags == 1:
            status = "conditional"
            rationale = "一部懸念があるが、条件付きで承認。"
            conditions = "指摘された課題の改善を次四半期で実施"
        else:
            status = "approved"
            rationale = "四半期レビューを承認。計画通りの進捗。"
            conditions = None

        return QuarterlyBoardReview(
            status=status,
            rationale=rationale,
            conditions=conditions,
            member_opinions=opinions,
        )