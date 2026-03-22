import json
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..models.agenda import Agenda
from .weekly_report_service import WeeklyReportService

class AgendaService:
    def __init__(self):
        self.members_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/members.json'))
        self.weekly_report_service = WeeklyReportService()

    def load_members(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.members_path):
            return []
        with open(self.members_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    def generate_weekly_agenda(self) -> Agenda:
        # 週次レポート情報の取得
        weekly_report = self.weekly_report_service.generate_weekly_report()
        
        # メンバー情報の取得
        members = self.load_members()
        
        # 高優先度タスクの抽出
        high_priority_tasks = [t for t in weekly_report.get('tasks', []) if t.get('priority') == 'high']
        
        # メンバーの課題を集約
        member_challenges = []
        for member in members:
            if member.get('challenges'):
                for challenge in member.get('challenges', []):
                    member_challenges.append(f"{member.get('name')}さんの課題: {challenge}")
        
        # トピックの生成
        topics = []
        topics.append("高優先度タスクの進捗確認")
        if high_priority_tasks:
            tasks_summary = ", ".join([t.get('title', '') for t in high_priority_tasks])
            topics.append(f"タスク進捗: {tasks_summary}")
        if member_challenges:
            topics.append("メンバーの課題共有")
        topics.append("プロジェクトのリスク確認")
        topics.append("今週の優先順位の再確認")
        
        # リスク・懸念点の生成
        risks = []
        if weekly_report.get('high_priority') > 0:
            risks.append(f"{weekly_report.get('high_priority')}件の高優先度タスクが未完了の可能性あり")
        if member_challenges:
            risks.append("複数のメンバーが課題を抱えている可能性")
        risks.append("スケジュール遅延のリスク")
        
        # 決定事項の提案
        decisions = [
            "今週の優先順位の確定",
            "メンバーのサポート体制の確認",
            "必要に応じて担当者の再アサイン"
        ]
        
        # 日付の設定（今週月曜）
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        date_str = monday.strftime("%Y-%m-%d")
        
        agenda = Agenda(
            title="今週のチームミーティングアジェンダ",
            date=date_str,
            topics=topics,
            risks=risks,
            decisions=decisions,
            notes="AI秘書が自動生成したアジェンダです"
        )
        
        return agenda