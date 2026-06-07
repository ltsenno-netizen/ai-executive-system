import json
import os
from typing import List, Optional

from .executive_simulation_engine import ExecutiveSimulationEngine
from .executive_simulation_repository import ExecutiveSimulationRepository
from .scenario_simulation_service import ScenarioSimulationService
from .strategy_engine_v2_service import StrategyEngineV2Service
from .multi_company_comparative_service import MultiCompanyComparativeService
from .meta_cognition_service import MetaCognitionService
from .corporate_memory_service import CorporateMemoryService
from ..models.executive_simulation_model import (
    ExecutiveSimulationInput,
    ExecutiveSimulationResult,
    StrategyBundle,
)
from ..models.corporate_memory_model import MemoryImportance, MemoryItemType
from ..models.strategy_engine_v2_model import StrategyEngineV2Report


class ExecutiveSimulationService:
    def __init__(self):
        self.engine = ExecutiveSimulationEngine()
        self.scenario_service = ScenarioSimulationService()
        self.strategy_service = StrategyEngineV2Service()
        self.comparison_service = MultiCompanyComparativeService()
        self.meta_service = MetaCognitionService()
        self.memory_service = CorporateMemoryService()
        self.repository = ExecutiveSimulationRepository()

    def run_simulation(self, sim_input: ExecutiveSimulationInput) -> ExecutiveSimulationResult:
        scenario_result = self.scenario_service.get_simulation_result(sim_input.scenario_type)
        if scenario_result is None:
            self.scenario_service.run_all_simulations()
            scenario_result = self.scenario_service.get_simulation_result(sim_input.scenario_type)

        if scenario_result is None:
            raise ValueError(f"Scenario result not found for type: {sim_input.scenario_type}")

        if sim_input.strategy_bundle_id:
            strategy_bundle = self._load_strategy_bundle(sim_input.strategy_bundle_id)
        else:
            strategy_report = self.strategy_service.run_strategy_for_scenario_type(sim_input.scenario_type)
            strategy_bundle = self._build_strategy_bundle(strategy_report)

        comparison_report = self.comparison_service.get_last_comparison()
        meta_report = self.meta_service.get_latest()

        result = self.engine.run_executive_simulation(
            sim_input=sim_input,
            strategy_bundle=strategy_bundle,
            scenario_result=scenario_result,
            comparison_report=comparison_report,
            meta_report=meta_report,
        )

        self.repository.save(result)
        self._record_simulation_memory(result)
        return result

    def get_latest(self) -> Optional[ExecutiveSimulationResult]:
        return self.repository.get_latest()

    def get_by_id(self, simulation_id: str) -> Optional[ExecutiveSimulationResult]:
        return self.repository.get_by_id(simulation_id)

    def list_recent(self, limit: int = 20) -> List[ExecutiveSimulationResult]:
        return self.repository.list_recent(limit)

    def export_simulation_markdown(self, simulation_id: str) -> Optional[str]:
        simulation = self.get_by_id(simulation_id)
        if simulation is None:
            return None

        lines = [
            f"# Executive Simulation Report {simulation.simulation_id}",
            f"**Scenario:** {simulation.scenario_type}",
            f"**Strategy Bundle:** {simulation.strategy_bundle_id}",
            f"**Consensus Level:** {simulation.consensus_level:.2f}",
            f"**Approved:** {simulation.approved}",
            "",
            "## CEO Summary",
            simulation.ceo_summary,
            "",
            "## Votes",
        ]
        for vote in simulation.votes:
            lines.append(f"- **{vote.role.value}**: {vote.stance.value} — {vote.rationale}")

        lines.extend(["", "## Comments"])
        for comment in simulation.comments:
            lines.append(f"### {comment.role.value}")
            lines.append(f"- Stance: {comment.stance.value}")
            if comment.key_points:
                lines.append(f"- Key points: {', '.join(comment.key_points)}")
            if comment.risks:
                lines.append(f"- Risks: {', '.join(comment.risks)}")
            if comment.opportunities:
                lines.append(f"- Opportunities: {', '.join(comment.opportunities)}")
            if comment.suggested_changes:
                lines.append(f"- Suggested changes: {', '.join(comment.suggested_changes)}")
            lines.append("")

        lines.append("## Minority Reports")
        for minority in simulation.minority_reports:
            lines.append(f"- {minority}")

        return "\n".join(lines)

    def _load_strategy_bundle(self, bundle_id: str) -> StrategyBundle:
        report = self.strategy_service.get_report_by_id(bundle_id)
        if report is None:
            raise ValueError(f"Strategy bundle not found: {bundle_id}")
        return self._build_strategy_bundle(report)

    def _build_strategy_bundle(self, report: StrategyEngineV2Report) -> StrategyBundle:
        return StrategyBundle(
            directive_id=report.report_id,
            scenario_type=report.scenario_type.value,
            executive_summary=report.executive_summary,
            directives=report.strategy_directives,
            recommended_actions=report.recommended_actions,
            context_notes=(report.scenario_insights[0] if report.scenario_insights else None),
        )

    def _record_simulation_memory(self, result: ExecutiveSimulationResult) -> None:
        try:
            self.memory_service.add_memory(
                item_type=MemoryItemType.EXECUTIVE_SIMULATION,
                title=f"Executive simulation {result.simulation_id}",
                description=f"Consensus {result.consensus_level:.2f}, approved={result.approved}",
                context={
                    "simulation_id": result.simulation_id,
                    "consensus_level": result.consensus_level,
                    "approved": result.approved,
                },
                importance=MemoryImportance.HIGH,
                tags=["EXECUTIVE_SIMULATION", "DECISION", "ROLE_PLAY"],
                related_entity_id=result.simulation_id,
                related_entity_type="ExecutiveSimulationResult",
            )
        except Exception:
            pass
