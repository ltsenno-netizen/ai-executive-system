import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.development import DevelopmentProgress, MonthlyReview, Achievement, DevelopmentMilestone
from ..models.member import Member
from ..models.task import Task
from .development_service import DevelopmentService

class DevelopmentProgressService:
    def __init__(self):
        self.progress_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/development_progress.json'))
        self.development_service = DevelopmentService()

    def load_progress_data(self) -> Dict[int, DevelopmentProgress]:
        if not os.path.exists(self.progress_path):
            return {}
        with open(self.progress_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        progress = {}
        for item in data:
            progress[item['member_id']] = DevelopmentProgress(**item)
        return progress

    def save_progress_data(self, progress_data: Dict[int, DevelopmentProgress]):
        data = [progress.dict() for progress in progress_data.values()]
        os.makedirs(os.path.dirname(self.progress_path), exist_ok=True)
        with open(self.progress_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_or_create_progress(self, member_id: int) -> Optional[DevelopmentProgress]:
        """メンバーの進捗状況を取得、なければ新規作成"""
        progress_data = self.load_progress_data()
        
        if member_id in progress_data:
            return progress_data[member_id]
        
        # 新規作成
        plan = self.development_service.generate_development_plan(member_id)
        if not plan:
            return None
        
        progress = DevelopmentProgress(
            member_id=member_id,
            member_name=plan.member_name,
            role=plan.role,
            plan_created_date=plan.created_date,
            current_month=1,
            overall_completion=0,
            monthly_reviews=[],
            upcoming_milestones=plan.milestones[:3],  # 次の3ヶ月分
            recommended_actions=self._generate_initial_actions(plan),
            last_updated=datetime.now().strftime("%Y-%m-%d")
        )
        
        progress_data[member_id] = progress
        self.save_progress_data(progress_data)
        return progress

    def generate_monthly_review(self, member_id: int, month: int, 
                               achievements: List[Dict[str, Any]], 
                               member_reflection: Optional[str] = None) -> Optional[MonthlyReview]:
        """月次レビューの生成"""
        plan = self.development_service.generate_development_plan(member_id)
        if not plan:
            return None
        
        # 達成度の計算
        achievement_objects = [Achievement(**ach) for ach in achievements]
        overall_progress = self._calculate_overall_progress(achievement_objects, plan)
        
        # 強み・課題の分析
        strengths, challenges = self._analyze_performance(achievement_objects, plan)
        
        # 次の月のフォーカス
        next_focus = self._generate_next_month_focus(month, plan, achievement_objects)
        
        # マネージャーフィードバックの生成
        manager_feedback = self._generate_manager_feedback(achievement_objects, overall_progress, plan)
        
        review = MonthlyReview(
            member_id=member_id,
            month=month,
            review_date=datetime.now().strftime("%Y-%m-%d"),
            achievements=achievement_objects,
            overall_progress=overall_progress,
            strengths_demonstrated=strengths,
            challenges_encountered=challenges,
            next_month_focus=next_focus,
            manager_feedback=manager_feedback,
            member_reflection=member_reflection
        )
        
        # 進捗データを更新
        self._update_progress_after_review(member_id, review, plan)
        
        return review

    def get_progress_summary(self, member_id: int) -> Optional[DevelopmentProgress]:
        """進捗状況のサマリーを取得"""
        return self.get_or_create_progress(member_id)

    def _calculate_overall_progress(self, achievements: List[Achievement], plan: Any) -> int:
        """全体進捗率の計算"""
        if not achievements:
            return 0
        
        total_completion = sum(ach.completion_percentage for ach in achievements)
        return min(100, total_completion // len(achievements))

    def _analyze_performance(self, achievements: List[Achievement], plan: Any) -> tuple[List[str], List[str]]:
        """パフォーマンス分析"""
        strengths = []
        challenges = []
        
        for achievement in achievements:
            if achievement.completion_percentage >= 80:
                strengths.append(f"{achievement.milestone_title}の目標達成度が高い")
            elif achievement.completion_percentage < 50:
                challenges.append(f"{achievement.milestone_title}の進捗が遅れている")
            
            # 残りの目標から課題を抽出
            if achievement.remaining_objectives:
                challenges.extend([f"未達成: {obj}" for obj in achievement.remaining_objectives[:2]])
        
        # デフォルト値
        if not strengths:
            strengths = ["継続的な努力が認められる"]
        if not challenges:
            challenges = ["さらなる成長の機会がある"]
        
        return strengths, challenges

    def _generate_next_month_focus(self, current_month: int, plan: Any, achievements: List[Achievement]) -> List[str]:
        """次の月のフォーカスを生成"""
        next_month = current_month + 1
        
        # 次のマイルストーンを取得
        next_milestones = [m for m in plan.milestones if m.month == next_month]
        if next_milestones:
            milestone = next_milestones[0]
            return [
                f"{milestone.title}の達成",
                f"主要活動: {', '.join(milestone.activities[:2])}",
                f"評価基準: {', '.join(milestone.evaluation_criteria[:2])}"
            ]
        
        # 最終月以降の場合
        return [
            "全体目標の振り返りと次のステップの検討",
            "継続的なスキル向上",
            "チーム貢献度のさらなる向上"
        ]

    def _generate_manager_feedback(self, achievements: List[Achievement], overall_progress: int, plan: Any) -> str:
        """マネージャーフィードバックの生成"""
        if overall_progress >= 80:
            feedback = "素晴らしい進捗です。これまでの努力が実を結んでいます。"
        elif overall_progress >= 60:
            feedback = "着実に成長が見られます。引き続きこの調子で進めましょう。"
        elif overall_progress >= 40:
            feedback = "一定の進捗が見られますが、課題もあります。サポートが必要な点があれば相談してください。"
        else:
            feedback = "期待された進捗に達していません。現在の状況を詳しくお聞かせください。"
        
        # 具体的なフィードバック追加
        completed_items = []
        for ach in achievements:
            if ach.completed_objectives:
                completed_items.extend(ach.completed_objectives[:1])
        
        if completed_items:
            feedback += f"\n\n特に良かった点: {', '.join(completed_items[:2])}"
        
        return feedback

    def _generate_initial_actions(self, plan: Any) -> List[str]:
        """初期推奨アクションの生成"""
        if not plan.milestones:
            return ["育成計画の詳細を確認してください"]
        
        first_milestone = plan.milestones[0]
        return [
            f"第1ヶ月: {first_milestone.title}を開始する",
            f"主要活動: {', '.join(first_milestone.activities[:2])}",
            "定期的な進捗確認を設定する"
        ]

    def _update_progress_after_review(self, member_id: int, review: MonthlyReview, plan: Any):
        """レビュー後の進捗データ更新"""
        progress_data = self.load_progress_data()
        progress = progress_data.get(member_id)
        if not progress:
            return
        
        # 月次レビューを追加
        progress.monthly_reviews.append(review)
        
        # 現在の月を更新
        progress.current_month = review.month
        
        # 全体完了率を更新
        progress.overall_completion = review.overall_progress
        
        # 次のマイルストーンを更新
        next_month = review.month + 1
        progress.upcoming_milestones = [m for m in plan.milestones if m.month >= next_month][:3]
        
        # 推奨アクションを更新
        progress.recommended_actions = review.next_month_focus
        
        # 更新日時
        progress.last_updated = review.review_date
        
        self.save_progress_data(progress_data)