import json
import os
from typing import List, Optional, Dict, Any
from ..models.quarterly_review_model import QuarterlyReview
from ..models.mid_term_plan_model import MidTermPlan
from ..models.ai_ceo_model import AICeoPersona
from ..services.ai_board_members import BaseBoardMember, FinancialDirector, BrandDirector, RiskDirector, OrgDirector
from .quarterly_review_engine import QuarterlyReviewEngine
from .mid_term_plan_service import MidTermPlanService
from .ceo_learning_service import CeoLearningService


class QuarterlyReviewService:
    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.reviews_path = os.path.join(self.data_path, 'reviews', 'quarterly')
        os.makedirs(self.reviews_path, exist_ok=True)
        self.engine = QuarterlyReviewEngine()
        self.mid_term_service = MidTermPlanService()
        self.ceo_service = CeoLearningService()

    def generate_quarterly_review(self, quarter: str) -> QuarterlyReview:
        # 1. 対象四半期の月次結果を取得
        monthly_results = self._get_quarterly_monthly_results(quarter)

        # 2. 最新の中期計画を取得
        mid_term_plan = self.mid_term_service.load_latest_plan()

        # 3. CEO Persona を取得
        ceo_persona = self.ceo_service.get_current_persona()

        # 4. Board メンバーを取得
        board_members = self._get_board_members()

        # 5. quarterly_review_engine.build_quarterly_review を呼ぶ
        review = self.engine.build_quarterly_review(
            quarter=quarter,
            monthly_results=monthly_results,
            mid_term_plan=mid_term_plan,
            ceo_persona=ceo_persona,
            board_members=board_members,
        )

        # 6. /reviews/quarterly/{quarter}.json / .md に保存
        self._save_review(review)

        # 7. QuarterlyReview を返す
        return review

    def get_quarterly_review(self, quarter: str) -> Optional[QuarterlyReview]:
        json_file = os.path.join(self.reviews_path, f'{quarter}.json')
        if not os.path.exists(json_file):
            return None

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return QuarterlyReview(**data)

    def get_latest_quarterly_review(self) -> Optional[QuarterlyReview]:
        if not os.path.exists(self.reviews_path):
            return None

        quarters = [f.replace('.json', '') for f in os.listdir(self.reviews_path) if f.endswith('.json')]
        if not quarters:
            return None

        latest_quarter = max(quarters)
        return self.get_quarterly_review(latest_quarter)

    def _get_quarterly_monthly_results(self, quarter: str) -> List[Dict[str, Any]]:
        # 四半期に含まれる月を特定（例: 2026-Q1 -> 2026-01, 2026-02, 2026-03）
        year, q = quarter.split('-Q')
        q_num = int(q)
        months = [f"{year}-{str((q_num-1)*3 + i+1).zfill(2)}" for i in range(3)]

        results = []
        for month in months:
            try:
                # monthly_batch_service から結果を取得（仮定）
                # 実際の実装では適切なサービスを使用
                result_file = os.path.join(self.data_path, 'monthly_results', f'{month}.json')
                if os.path.exists(result_file):
                    with open(result_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    results.append(data)
            except Exception:
                # 月次結果がない場合はスキップ
                continue

        return results

    def _get_board_members(self) -> List[BaseBoardMember]:
        return [
            FinancialDirector(),
            BrandDirector(),
            RiskDirector(),
            OrgDirector(),
        ]

    def _save_review(self, review: QuarterlyReview) -> None:
        # JSON 保存
        json_file = os.path.join(self.reviews_path, f'{review.quarter}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(review.model_dump_json(indent=2, ensure_ascii=False))

        # Markdown 保存
        md_file = os.path.join(self.reviews_path, f'{review.quarter}.md')
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown(review))

    def _generate_markdown(self, review: QuarterlyReview) -> str:
        lines = [
            f'# 四半期レビュー（{review.quarter}）',
            '',
            '## 1. 財務総括',
            f'- 売上合計: ¥{review.financial.revenue_total:,.0f}M （計画比 {review.financial.revenue_vs_plan:+.1%}）',
            f'- 営業利益: ¥{review.financial.operating_profit_total:,.0f}M （計画比 {review.financial.profit_vs_plan:+.1%}）',
            f'- 期末キャッシュ: ¥{review.financial.cash_end:,.0f}M',
            '',
            '## 2. 実行サマリ',
            f'- 完了施策: {review.execution.initiatives_completed}',
            f'- 遅延施策: {review.execution.initiatives_delayed}',
            f'- 組織負荷指数: {review.execution.org_load_index:.2f}',
            '',
            '## 3. ギャップ分析',
            review.gap_analysis,
            '',
            '## 4. 次四半期の重点テーマ',
        ]

        for focus in review.next_quarter_focus:
            lines.append(f'- {focus}')

        lines.extend([
            '',
            '## 5. 取締役会レビュー',
            f'- 判定: {review.board_review.status}',
            f'- 理由: {review.board_review.rationale}',
        ])

        if review.board_review.conditions:
            lines.append(f'- 条件: {review.board_review.conditions}')

        # 取締役意見の追加
        if review.board_review.member_opinions:
            lines.append('')
            lines.append('### 取締役個別意見')
            for op in review.board_review.member_opinions:
                risk_note = ' (リスク指摘)' if op.risk_flag else ''
                lines.append(f'- **{op.member_role}**: {op.rationale}{risk_note}')

        return '\n'.join(lines)