import json
import os
from typing import List, Dict, Any
from ..models.task import Task

class WeeklyReportService:
    def __init__(self):
        self.data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/tasks.json'))

    def load_tasks(self) -> List[Task]:
        if not os.path.exists(self.data_path):
            return []
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [Task(**item) for item in data]

    def generate_weekly_report(self) -> Dict[str, Any]:
        tasks = self.load_tasks()
        
        # 優先度でソート
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_tasks = sorted(tasks, key=lambda t: priority_order.get(t.priority, 3))
        
        # レポート生成
        report = {
            "week_start": "2026-03-17",  # 仮の週開始日
            "week_end": "2026-03-23",
            "total_tasks": len(tasks),
            "high_priority": len([t for t in tasks if t.priority == 'high']),
            "medium_priority": len([t for t in tasks if t.priority == 'medium']),
            "low_priority": len([t for t in tasks if t.priority == 'low']),
            "tasks": [task.dict() for task in sorted_tasks],
            "summary": "今週のタスク状況です。高優先度のタスクに注力してください。"
        }
        return report