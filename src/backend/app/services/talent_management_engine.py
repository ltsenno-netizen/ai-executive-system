import json
import os
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from ..models.talent_management_extended import (
    DepartmentMission,
    RoleDefinition,
    TaskInstance,
    IncidentInstance,
    ProcessDefinition,
    RACIEntry,
    TaskTemplate
)

class SimulationReport:
    def __init__(self, days_simulated: int, tasks_completed: List[str], incidents_occurred: List[str],
                 kpi_changes: Dict[str, float], pl_impact: Dict[str, float]):
        self.days_simulated = days_simulated
        self.tasks_completed = tasks_completed
        self.incidents_occurred = incidents_occurred
        self.kpi_changes = kpi_changes
        self.pl_impact = pl_impact

class TalentManagementEngine:
    """タレントマネジメント部インバスケット運用エンジン"""

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.reports_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../reports')
        )
        os.makedirs(self.reports_path, exist_ok=True)

        # ファイルパス
        self.mission_file = os.path.join(self.data_path, 'talent_management_mission.json')
        self.roles_file = os.path.join(self.data_path, 'talent_management_roles.json')
        self.task_templates_file = os.path.join(self.data_path, 'talent_management_task_templates.json')
        self.incidents_file = os.path.join(self.data_path, 'talent_management_incidents.json')
        self.processes_file = os.path.join(self.data_path, 'process_definitions.json')
        self.raci_file = os.path.join(self.data_path, 'raci_talent.json')

        # インメモリストレージ
        self.task_instances: Dict[str, TaskInstance] = {}
        self.incident_instances: Dict[str, IncidentInstance] = {}
        self.members: Dict[str, dict] = {}  # 簡易メンバー管理

    def load_missions(self) -> DepartmentMission:
        """部門ミッションを読み込む"""
        if not os.path.exists(self.mission_file):
            raise FileNotFoundError(f"Mission data not found: {self.mission_file}")

        with open(self.mission_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return DepartmentMission(**data)

    def load_role_definitions(self) -> List[RoleDefinition]:
        """役割定義を読み込む"""
        if not os.path.exists(self.roles_file):
            raise FileNotFoundError(f"Roles data not found: {self.roles_file}")

        with open(self.roles_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [RoleDefinition(**role) for role in data]

    def load_task_templates(self) -> List[TaskTemplate]:
        """タスクテンプレートを読み込む"""
        if not os.path.exists(self.task_templates_file):
            raise FileNotFoundError(f"Task templates not found: {self.task_templates_file}")

        with open(self.task_templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [TaskTemplate(**task) for task in data]

    def load_process_definitions(self) -> List[ProcessDefinition]:
        """プロセス定義を読み込む"""
        if not os.path.exists(self.processes_file):
            raise FileNotFoundError(f"Process definitions not found: {self.processes_file}")

        with open(self.processes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [ProcessDefinition(**process) for process in data]

    def load_raci_entries(self) -> List[RACIEntry]:
        """RACIエントリを読み込む"""
        if not os.path.exists(self.raci_file):
            raise FileNotFoundError(f"RACI data not found: {self.raci_file}")

        with open(self.raci_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [RACIEntry(**entry) for entry in data]

    def instantiate_task(self, template_id: str, related_project: Optional[str] = None) -> TaskInstance:
        """タスクテンプレートからタスクインスタンスを生成"""
        templates = self.load_task_templates()
        template = next((t for t in templates if t.id == template_id), None)

        if not template:
            raise ValueError(f"Template not found: {template_id}")

        task_id = f"task_{uuid.uuid4().hex[:8]}"
        due_date = datetime.now() + timedelta(hours=template.estimated_hours * 2)  # 緩めの期限

        task = TaskInstance(
            id=task_id,
            template_id=template_id,
            title=template.title,
            description=template.description,
            priority=template.priority,
            required_roles=template.required_roles,
            estimated_hours=template.estimated_hours,
            status="Open",
            created_at=datetime.now(),
            due_date=due_date,
            related_project=related_project,
            pl_impact=self._generate_pl_impact(template_id)
        )

        self.task_instances[task_id] = task
        return task

    def assign_task(self, task_id: str, member_id: str) -> bool:
        """タスクをメンバーに割当"""
        if task_id not in self.task_instances:
            return False

        if member_id not in self.members:
            return False

        task = self.task_instances[task_id]
        member = self.members[member_id]

        # ロールチェック
        if member['role'] not in task.required_roles:
            return False

        task.assigned_to = member_id
        task.status = "InProgress"
        return True

    def progress_task(self, task_id: str, hours: int) -> TaskInstance:
        """タスクの進捗を更新"""
        if task_id not in self.task_instances:
            raise ValueError(f"Task not found: {task_id}")

        task = self.task_instances[task_id]

        # 簡易進捗ロジック（経験値と優先度に基づく）
        if task.assigned_to:
            member = self.members[task.assigned_to]
            experience_factor = min(member['experience_years'] / 10, 1.0)
            progress_rate = 0.1 + (experience_factor * 0.3)  # 10-40% per hour

            # タスク完了判定（簡易）
            if self.random.random() < progress_rate * hours:
                task.status = "Done"

        return task

    def create_incident(self, scenario_id: str) -> IncidentInstance:
        """インシデントを生成"""
        incidents = self._load_incident_scenarios()
        scenario = next((i for i in incidents if i.id == scenario_id), None)

        if not scenario:
            raise ValueError(f"Scenario not found: {scenario_id}")

        incident_id = f"incident_{uuid.uuid4().hex[:8]}"

        incident = IncidentInstance(
            id=incident_id,
            scenario_id=scenario_id,
            title=scenario.title,
            severity=scenario.severity,
            occurred_at=datetime.now(),
            status="Open",
            impact_estimate=self._estimate_impact(scenario.severity),
            escalated_to=None
        )

        self.incident_instances[incident_id] = incident
        return incident

    def escalate_incident(self, incident_id: str, to_role: str) -> bool:
        """インシデントをエスカレーション"""
        if incident_id not in self.incident_instances:
            return False

        incident = self.incident_instances[incident_id]
        incident.escalated_to = to_role
        incident.status = "Escalated"
        return True

    def run_simulation_step(self, days: int, seed: Optional[int] = None) -> SimulationReport:
        """シミュレーションを実行"""
        if seed is not None:
            self.random = random.Random(seed)

        tasks_completed = []
        incidents_occurred = []
        kpi_changes = {}
        pl_impact = {"total_revenue": 0, "total_cost": 0, "net_profit": 0}

        for day in range(days):
            # タスク進捗
            for task_id, task in list(self.task_instances.items()):
                if task.status == "InProgress":
                    self.progress_task(task_id, 8)  # 1日8時間作業
                    if task.status == "Done":
                        tasks_completed.append(f"{task.title} ({task.assigned_to})")
                        if task.pl_impact:
                            for key, value in task.pl_impact.items():
                                pl_impact[key] += value

            # インシデント発生
            self._generate_random_incidents(incidents_occurred)

            # KPI計算
            kpi_changes[f"day_{day+1}"] = self._calculate_daily_kpis()

        # レポート保存
        report = SimulationReport(days, tasks_completed, incidents_occurred, kpi_changes, pl_impact)
        self._save_simulation_report(report)

        return report

    def _load_incident_scenarios(self) -> List[dict]:
        """インシデントシナリオを読み込む（既存ファイルから）"""
        incidents_file = os.path.join(self.data_path, 'talent_management_incidents.json')
        if not os.path.exists(incidents_file):
            return []

        with open(incidents_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _generate_pl_impact(self, template_id: str) -> Dict[str, float]:
        """タスクのPL影響を生成"""
        impacts = {
            "task_estimation": {"total_revenue": 1000, "total_cost": 200, "net_profit": 800},
            "task_contract_negotiation": {"total_revenue": 2000, "total_cost": 300, "net_profit": 1700},
            "task_ltv_report": {"total_revenue": 500, "total_cost": 150, "net_profit": 350},
            "task_crisis_management": {"total_revenue": -500, "total_cost": 800, "net_profit": -1300},
        }
        return impacts.get(template_id, {"total_revenue": 0, "total_cost": 0, "net_profit": 0})

    def _estimate_impact(self, severity: str) -> str:
        """インシデントの影響を推定"""
        impacts = {
            "Critical": "収益損失1000万円以上、ブランド価値重大損失",
            "High": "収益損失500万円程度、ブランド価値損失",
            "Medium": "収益損失100万円程度、一時的な影響",
            "Low": "軽微な影響、対応コストのみ"
        }
        return impacts.get(severity, "影響不明")

    def _generate_random_incidents(self, incidents_list: List[str]):
        """ランダムにインシデントを発生"""
        scenarios = self._load_incident_scenarios()
        for scenario in scenarios:
            severity_rates = {"Critical": 0.01, "High": 0.05, "Medium": 0.1, "Low": 0.2}
            rate = severity_rates.get(scenario.severity, 0.05)

            if self.random.random() < rate:
                incident = self.create_incident(scenario.id)
                incidents_list.append(f"{incident.title} ({incident.severity})")

    def _calculate_daily_kpis(self) -> Dict[str, float]:
        """日次KPIを計算"""
        total_tasks = len(self.task_instances)
        completed_tasks = len([t for t in self.task_instances.values() if t.status == "Done"])
        active_incidents = len([i for i in self.incident_instances.values() if i.status in ["Open", "Escalated"]])

        return {
            "task_completion_rate": completed_tasks / max(total_tasks, 1),
            "active_incidents": active_incidents,
            "average_task_age": 1.5,  # 仮定値
            "resource_utilization": 0.85  # 仮定値
        }

    def _save_simulation_report(self, report: SimulationReport):
        """シミュレーションレポートを保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulation_report_{timestamp}.json"

        report_data = {
            "days_simulated": report.days_simulated,
            "tasks_completed": report.tasks_completed,
            "incidents_occurred": report.incidents_occurred,
            "kpi_changes": report.kpi_changes,
            "pl_impact": report.pl_impact,
            "generated_at": datetime.now().isoformat()
        }

        filepath = os.path.join(self.reports_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)