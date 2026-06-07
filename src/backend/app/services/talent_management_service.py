import json
import os
import random
from typing import List, Dict, Optional
from ..models.talent_management import (
    UnitDefinition,
    TaskTemplate,
    IncidentScenario,
    MemberProfile,
    UnitState,
    DepartmentMission
)

class SimulationResult:
    def __init__(self, completed_tasks: List[str], new_incidents: List[str], kpi_changes: Dict[str, float]):
        self.completed_tasks = completed_tasks
        self.new_incidents = new_incidents
        self.kpi_changes = kpi_changes

class TalentManagementService:
    """タレントマネジメント部仮想オフィスサービス"""

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.units_file = os.path.join(self.data_path, 'talent_management_units.json')
        self.tasks_file = os.path.join(self.data_path, 'talent_management_tasks.json')
        self.incidents_file = os.path.join(self.data_path, 'talent_management_incidents.json')

        # インメモリストレージ（実際の運用ではDBを使用）
        self.members: Dict[str, MemberProfile] = {}
        self.unit_states: Dict[str, UnitState] = {}

    def load_units(self) -> List[UnitDefinition]:
        """全ユニット定義を読み込む"""
        if not os.path.exists(self.units_file):
            raise FileNotFoundError(f"Units data not found: {self.units_file}")

        with open(self.units_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [UnitDefinition(**unit) for unit in data]

    def load_tasks(self) -> List[TaskTemplate]:
        """全タスクテンプレートを読み込む"""
        if not os.path.exists(self.tasks_file):
            raise FileNotFoundError(f"Tasks data not found: {self.tasks_file}")

        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [TaskTemplate(**task) for task in data]

    def load_incidents(self) -> List[IncidentScenario]:
        """全インシデントシナリオを読み込む"""
        if not os.path.exists(self.incidents_file):
            raise FileNotFoundError(f"Incidents data not found: {self.incidents_file}")

        with open(self.incidents_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [IncidentScenario(**incident) for incident in data]

    def assign_task_to_member(self, task_id: str, member_id: str) -> bool:
        """タスクをメンバーに割当"""
        if member_id not in self.members:
            return False

        member = self.members[member_id]
        tasks = self.load_tasks()
        task = next((t for t in tasks if t.id == task_id), None)

        if not task:
            return False

        # ロールチェック
        if member.role not in task.required_roles:
            return False

        # タスク割当
        member.current_tasks.append(task_id)
        return True

    def simulate_time_advance(self, months: int) -> SimulationResult:
        """時間を進めてシミュレーションを実行"""
        completed_tasks = []
        new_incidents = []
        kpi_changes = {}

        # 各月のシミュレーション
        for month in range(months):
            # タスク完了処理
            for member_id, member in self.members.items():
                if member.current_tasks:
                    # 経験値と優先度に基づく完了確率
                    experience_factor = min(member.experience_years / 10, 1.0)
                    completion_rate = 0.3 + (experience_factor * 0.4)  # 30-70%

                    for task_id in member.current_tasks[:]:
                        if self.random.random() < completion_rate:
                            member.current_tasks.remove(task_id)
                            completed_tasks.append(f"{member.name}: {task_id}")

            # インシデント発生
            incidents = self.load_incidents()
            for incident in incidents:
                # severityに応じた発生確率
                severity_rates = {"Critical": 0.05, "High": 0.1, "Medium": 0.2, "Low": 0.3}
                rate = severity_rates.get(incident.severity, 0.1)

                if self.random.random() < rate:
                    new_incidents.append(f"{incident.title} ({incident.severity})")

            # KPI変化（簡易計算）
            kpi_changes[f"month_{month+1}"] = {
                "task_completion_rate": len(completed_tasks) / max(len(self.members), 1),
                "incident_count": len(new_incidents),
                "member_utilization": sum(len(m.current_tasks) for m in self.members.values()) / max(len(self.members), 1)
            }

        return SimulationResult(completed_tasks, new_incidents, kpi_changes)

    def evaluate_kpis(self, unit_name: str) -> Dict[str, float]:
        """ユニットのKPIを評価"""
        # 簡易KPI計算
        unit_members = [m for m in self.members.values() if m.role in self._get_unit_roles(unit_name)]
        total_tasks = sum(len(m.current_tasks) for m in unit_members)
        active_members = len([m for m in unit_members if m.current_tasks])

        return {
            "task_completion_rate": 0.85,  # 仮定値
            "incident_response_time": 2.3,  # 日数
            "member_satisfaction": 4.2,     # 5段階
            "kpi_achievement_rate": 0.92    # パーセント
        }

    def generate_inbasket_for_unit(self, unit_name: str, n: int) -> List[TaskTemplate]:
        """ユニット向けのインバスケットを生成"""
        all_tasks = self.load_tasks()
        unit_roles = self._get_unit_roles(unit_name)

        # 該当ロールのタスクをフィルタリング
        relevant_tasks = [t for t in all_tasks if any(role in t.required_roles for role in unit_roles)]

        # 優先度に基づいて重み付けして選択
        priority_weights = {"High": 3, "Medium": 2, "Low": 1}
        weighted_tasks = []
        for task in relevant_tasks:
            weight = priority_weights.get(task.priority, 1)
            weighted_tasks.extend([task] * weight)

        # n個選択（重複可）
        selected = []
        for _ in range(n):
            if weighted_tasks:
                selected.append(self.random.choice(weighted_tasks))

        return selected

    def create_member(self, profile: MemberProfile) -> bool:
        """仮想メンバーを作成"""
        if profile.id in self.members:
            return False

        self.members[profile.id] = profile
        return True

    def _get_unit_roles(self, unit_name: str) -> List[str]:
        """ユニット名からロールを取得"""
        units = self.load_units()
        unit = next((u for u in units if u.name == unit_name), None)
        return unit.roles if unit else []