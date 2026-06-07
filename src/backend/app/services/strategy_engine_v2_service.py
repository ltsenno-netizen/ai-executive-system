import json
import os
from typing import List, Optional

from ..models.strategy_engine_v2_model import (
    StrategyEngineV2Report,
)
from .strategy_engine_v2 import StrategyEngineV2
from .scenario_simulation_service import ScenarioSimulationService
from .corporate_intent_service import CorporateIntentService
from .frontier_optimization_service import FrontierOptimizationService
from .corporate_consciousness_service import CorporateConsciousnessService
from .corporate_memory_service import CorporateMemoryService
from ..models.corporate_memory_model import MemoryItemType


class StrategyEngineV2Service:
    """Service layer for the Corporate Strategy Engine 2.0."""

    def __init__(self):
        self.engine = StrategyEngineV2()
        self.scenario_service = ScenarioSimulationService()
        self.intent_service = CorporateIntentService()
        self.frontier_service = FrontierOptimizationService()
        self.consciousness_service = CorporateConsciousnessService()
        self.memory_service = CorporateMemoryService()
        self.storage_dir = os.path.join(os.path.dirname(__file__), '../../../data/strategy_engine_v2')
        os.makedirs(self.storage_dir, exist_ok=True)

    def run_strategy_for_scenario_type(self, scenario_type: str) -> StrategyEngineV2Report:
        result = self.scenario_service.get_simulation_result(scenario_type)
        if result is None:
            self.scenario_service.run_all_simulations()
            result = self.scenario_service.get_simulation_result(scenario_type)

        if result is None:
            raise ValueError(f"Scenario result not found for type: {scenario_type}")

        intent = self.intent_service.get_intent()
        frontier_health = self.frontier_service.get_frontier_health_score()
        try:
            consciousness_summary = self.consciousness_service.get_consciousness_summary("2026-01")
        except Exception:
            consciousness_summary = None

        report = self.engine.generate_strategy_report(
            simulation_result=result,
            intent=intent,
            frontier_health_score=frontier_health,
            consciousness_summary=consciousness_summary,
        )

        self._save_report(report)
        self._record_strategy_memory(report)
        return report

    def get_report(self, scenario_type: str) -> Optional[StrategyEngineV2Report]:
        filepath = os.path.join(self.storage_dir, f"{scenario_type}.json")
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return StrategyEngineV2Report(**data)

    def get_latest_report(self) -> Optional[StrategyEngineV2Report]:
        reports = self.get_all_reports()
        return reports[0] if reports else None

    def get_report_by_id(self, report_id: str) -> Optional[StrategyEngineV2Report]:
        for report in self.get_all_reports():
            if report.report_id == report_id:
                return report
        return None

    def get_all_reports(self) -> List[StrategyEngineV2Report]:
        reports: List[StrategyEngineV2Report] = []
        for filename in os.listdir(self.storage_dir):
            if not filename.endswith('.json'):
                continue
            filepath = os.path.join(self.storage_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    reports.append(StrategyEngineV2Report(**data))
            except Exception:
                continue
        return sorted(reports, key=lambda report: report.generated_at, reverse=True)

    def export_report_markdown(self, scenario_type: str) -> Optional[str]:
        report = self.get_report(scenario_type)
        if report is None:
            return None

        lines = [
            f"# Strategy Engine V2 Report — {report.scenario_type.value}",
            f"Generated at: {report.generated_at.isoformat()}",
            "",
            "## Executive Summary",
            report.executive_summary,
            "",
            "## Key Scores",
            f"- Alignment: {report.alignment_score:.3f}",
            f"- Risk / Resilience: {report.risk_resilience_score:.3f}",
            f"- Growth Commitment: {report.growth_commitment_score:.3f}",
            f"- Frontier Health: {report.frontier_health_score:.3f}",
            f"- Consciousness Alignment: {report.consciousness_alignment_score:.3f}",
            "",
            "## Strategic Directives",
        ]
        for directive in report.strategy_directives:
            lines.append(f"- **{directive.name}** ({directive.directive_type}, priority={directive.priority:.2f}): {directive.description}")

        lines.append("")
        lines.append("## Strategic Assets")
        for asset in report.strategic_assets:
            lines.append(f"- **{asset.name}** ({asset.asset_type}, priority={asset.priority:.2f}): {asset.description}")

        lines.append("")
        lines.append("## Recommended Actions")
        for action in report.recommended_actions:
            lines.append(f"- {action}")

        lines.append("")
        lines.append("## Scenario Insights")
        for insight in report.scenario_insights:
            lines.append(f"- {insight}")

        return "\n".join(lines)

    def _save_report(self, report: StrategyEngineV2Report) -> None:
        filepath = os.path.join(self.storage_dir, f"{report.scenario_type.value}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2, ensure_ascii=False, default=str)

    def _record_strategy_memory(self, report: StrategyEngineV2Report) -> None:
        try:
            self.memory_service.add_memory(
                item_type=MemoryItemType.STRATEGY_EXECUTED,
                title=f"Strategy Engine V2 report for {report.scenario_type.value}",
                description=report.executive_summary,
                context={
                    "scenario_type": report.scenario_type.value,
                    "alignment_score": report.alignment_score,
                    "risk_resilience_score": report.risk_resilience_score,
                },
                importance=None,
                tags=["strategy_engine_v2", report.scenario_type.value],
                related_entity_id=report.report_id,
                related_entity_type="StrategyEngineV2Report",
            )
        except Exception:
            pass
