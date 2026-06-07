import json
from pathlib import Path
from typing import List, Optional

from .meta_cognition_engine import MetaCognitionEngine
from .corporate_intent_service import CorporateIntentService
from .executive_agent_service import ExecutiveAgentService
from .autonomous_enterprise_service import AutonomousEnterpriseService
from .frontier_optimization_service import FrontierOptimizationService
from .corporate_consciousness_service import CorporateConsciousnessService
from .corporate_consciousness_evolution_service import CorporateConsciousnessEvolutionService
from .narrative_intelligence_service import NarrativeIntelligenceService
from .corporate_memory_service import CorporateMemoryService
from ..models.corporate_memory_model import MemoryImportance, MemoryItemType
from ..models.meta_cognition_model import MetaCognitionReport


class MetaCognitionService:
    DATA_DIR = Path("data/meta_cognition")
    REPORTS_FILE = Path("data/meta_cognition/reports.json")

    def __init__(self):
        self.engine = MetaCognitionEngine()
        self.intent_service = CorporateIntentService()
        self.agent_service = ExecutiveAgentService()
        self.autonomous_service = AutonomousEnterpriseService()
        self.frontier_service = FrontierOptimizationService()
        self.consciousness_service = CorporateConsciousnessService()
        self.evolution_service = CorporateConsciousnessEvolutionService()
        self.narrative_service = NarrativeIntelligenceService()
        self.memory_service = CorporateMemoryService()
        self.reports: List[MetaCognitionReport] = []

        self._ensure_data_directory()
        self._load_reports()

    def _ensure_data_directory(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load_reports(self):
        if self.REPORTS_FILE.exists():
            try:
                with open(self.REPORTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.reports = [MetaCognitionReport(**item) for item in data]
            except Exception:
                self.reports = []
        else:
            self.reports = []

    def _save_reports(self):
        self._ensure_data_directory()
        with open(self.REPORTS_FILE, "w", encoding="utf-8") as f:
            json.dump([report.model_dump() for report in self.reports], f, indent=2, default=str)

    def _save_report_to_memory(self, report: MetaCognitionReport) -> None:
        try:
            self.memory_service.add_memory(
                item_type=MemoryItemType.META_COGNITION,
                title="Meta-Cognition Assessment",
                description=(
                    f"Overall meta-cognition score {report.overall_score:.2f}. "
                    f"Detected biases: {', '.join(b.name for b in report.biases) or 'none'}."
                ),
                context={
                    "report_id": report.report_id,
                    "overall_score": report.overall_score,
                    "bias_names": [bias.name for bias in report.biases],
                },
                importance=MemoryImportance.HIGH,
                tags=["META_COGNITION", "SELF_EVALUATION"],
            )
        except Exception:
            pass

    def run_assessment(self, save_to_memory: bool = True) -> MetaCognitionReport:
        intent = self.intent_service.get_intent()
        agents = self.agent_service.get_agents()
        autonomous_history = self.autonomous_service.get_cycle_history()
        autonomous_metrics = self.autonomous_service.get_autonomous_metrics()
        frontier = self.frontier_service.get_current_frontier()
        frontier_summary = self.frontier_service.get_optimization_summary()
        consciousness = self.consciousness_service.get_latest_consciousness()
        evolution_state = self.evolution_service.get_state()
        evolution_history = self.evolution_service.get_evolution_history(limit=10)
        narratives = self.narrative_service.get_narrative_history(limit=20)
        memory_summary = self.memory_service.get_memory_summary(max_recent=5, max_critical=3)

        report = self.engine.build_meta_cognition_report(
            intent=intent,
            agents=agents,
            autonomous_history=autonomous_history.cycles if autonomous_history else None,
            autonomous_metrics=autonomous_metrics,
            frontier=frontier,
            frontier_summary=frontier_summary,
            consciousness=consciousness,
            evolution_state=evolution_state,
            evolution_history=evolution_history,
            narratives=narratives,
            memory_summary=memory_summary.model_dump() if memory_summary else None,
        )

        self.reports.append(report)
        self._save_reports()

        if save_to_memory:
            self._save_report_to_memory(report)

        return report

    def get_latest(self) -> Optional[MetaCognitionReport]:
        if self.reports:
            return self.reports[-1]
        return None

    def get_history(self) -> List[MetaCognitionReport]:
        return list(self.reports)

    def get_report(self, report_id: str) -> Optional[MetaCognitionReport]:
        return next((report for report in self.reports if report.report_id == report_id), None)

    def export_report_markdown(self, report_id: str) -> Optional[str]:
        report = self.get_report(report_id)
        if not report:
            return None

        lines = [
            f"# Meta-Cognition Report {report.report_id}",
            f"**Overall score:** {report.overall_score:.2f}",
            f"**Assessed at:** {report.timestamp.isoformat()}",
            "",
            "## Dimension scores",
        ]

        for score in report.scores:
            lines.append(f"- **{score.dimension.value}**: {score.score:.2f} (confidence {score.confidence:.2f})")
            lines.append(f"  - {score.rationale}")

        lines.append("")
        lines.append("## Detected biases")
        if report.biases:
            for bias in report.biases:
                lines.append(f"- **{bias.name}** ({bias.severity:.2f}): {bias.description}")
        else:
            lines.append("- None detected")

        lines.append("")
        lines.append("## Recommendations")
        for recommendation in report.recommendations:
            lines.append(f"- {recommendation}")

        return "\n".join(lines)
