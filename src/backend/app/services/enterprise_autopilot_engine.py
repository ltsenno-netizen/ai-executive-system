from datetime import datetime
from typing import Dict, List, Optional

from ..models.enterprise_autopilot_model import AutopilotCyclePhase, AutopilotCycleResult, AutopilotPhaseResult
from ..models.scenario_simulation_model import ScenarioSimulationResult
from ..models.multi_company_comparative_model import CompanyId
from ..models.corporate_memory_model import MemoryImportance, MemoryItemType
from .corporate_consciousness_service import CorporateConsciousnessService
from .corporate_consciousness_evolution_service import CorporateConsciousnessEvolutionService
from .external_environment_service_v2 import ExternalEnvironmentServiceV2
from .frontier_optimization_service import FrontierOptimizationService
from .scenario_simulation_service import ScenarioSimulationService
from .multi_company_comparative_service import MultiCompanyComparativeService
from .strategy_engine_v2_service import StrategyEngineV2Service
from .meta_cognition_service import MetaCognitionService
from .corporate_memory_service import CorporateMemoryService


class DecisionLogService:
    """Lightweight decision logging helper for autopilot cycles."""

    def __init__(self):
        self.log_dir = 'data/enterprise_autopilot/logs'
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        import os

        os.makedirs(self.log_dir, exist_ok=True)

    def log(self, cycle_id: str, message: str) -> None:
        path = f"{self.log_dir}/{cycle_id}.log"
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.utcnow().isoformat()}] {message}\n")


class LearningService:
    """Simple learning adapter for autopilot cycles."""

    def update_from_cycle(self, cycle: AutopilotCycleResult) -> Dict[str, object]:
        return {
            "learning_observations": [
                "Reinforce scenario monitoring cadence.",
                "Calibrate strategy recommendations based on latest meta-cognition feedback.",
            ],
            "recommended_followups": [
                "Review high-risk scenario assumptions.",
                "Schedule quarterly multi-company comparison updates.",
            ],
        }


class EnterpriseAutopilotEngine:
    """Enterprise Autopilot orchestration engine for periodic cycle execution."""

    def __init__(self):
        self.consciousness_service = CorporateConsciousnessService()
        self.evolution_service = CorporateConsciousnessEvolutionService()
        self.frontier_service = FrontierOptimizationService()
        self.environment_service = ExternalEnvironmentServiceV2()
        self.scenario_service = ScenarioSimulationService()
        self.multi_company_service = MultiCompanyComparativeService()
        self.strategy_service = StrategyEngineV2Service()
        self.meta_cognition_service = MetaCognitionService()
        self.memory_service = CorporateMemoryService()
        self.decision_logger = DecisionLogService()
        self.learning_service = LearningService()

    def run_autopilot_cycle(self, cycle_id: str) -> AutopilotCycleResult:
        result = AutopilotCycleResult(cycle_id=cycle_id, overall_status="STARTED")
        try:
            perception = self.run_perception()
            result.phases.append(perception)
            self.decision_logger.log(cycle_id, "Completed perception phase.")

            evaluation = self.run_evaluation()
            result.phases.append(evaluation)
            self.decision_logger.log(cycle_id, "Completed evaluation phase.")

            prediction = self.run_prediction()
            result.phases.append(prediction)
            self.decision_logger.log(cycle_id, "Completed prediction phase.")

            comparison = self.run_comparison()
            result.phases.append(comparison)
            self.decision_logger.log(cycle_id, "Completed comparison phase.")

            strategy = self.run_strategy(prediction)
            result.phases.append(strategy)
            self.decision_logger.log(cycle_id, "Completed strategy phase.")

            execution = self.run_execution(strategy)
            result.phases.append(execution)
            self.decision_logger.log(cycle_id, "Completed execution phase.")

            learning = self.run_learning(result)
            result.phases.append(learning)
            self.decision_logger.log(cycle_id, "Completed learning phase.")

            result.overall_status = "COMPLETED"
            result.summary = self._build_cycle_summary(result)
            result.key_actions = self._build_key_actions(result)
            result.experience_notes = self._build_experience_notes(result)
            result.cycle_metrics = self._build_cycle_metrics(result)
        except Exception as exc:
            result.overall_status = "FAILED"
            result.summary = f"Enterprise Autopilot cycle failed: {str(exc)}"
            result.key_actions = ["Review cycle failure and alert leadership."]
            self.decision_logger.log(cycle_id, f"Cycle failed: {exc}")
        finally:
            result.completed_at = datetime.utcnow()

        return result

    def run_perception(self) -> AutopilotPhaseResult:
        try:
            consciousness = self.consciousness_service.get_latest_consciousness()
            if consciousness is None:
                consciousness = self.consciousness_service.generate_consciousness(
                    period="2026-01",
                    strategic_intent="Enterprise Autopilot default intent",
                )
        except Exception:
            consciousness = None

        try:
            environment = self.environment_service.get_latest_environment()
            if environment is None:
                environment = self.environment_service.get_environment("2026-01")
        except Exception:
            environment = None

        memory_summary = None
        try:
            memory_summary = self.memory_service.get_memory_summary(max_recent=3, max_critical=2)
        except Exception:
            memory_summary = None

        details = {
            "consciousness": getattr(consciousness, 'summary', str(consciousness)) if consciousness is not None else None,
            "environment": getattr(environment, 'period', None),
            "memory_summary_count": getattr(memory_summary, 'total_memories', None),
        }

        return AutopilotPhaseResult(
            phase=AutopilotCyclePhase.PERCEPTION,
            summary="Observing current organizational state, consciousness, environment, and memory context.",
            details=details,
            succeeded=True,
        )

    def run_evaluation(self) -> AutopilotPhaseResult:
        report = self.meta_cognition_service.run_assessment()
        return AutopilotPhaseResult(
            phase=AutopilotCyclePhase.EVALUATION,
            summary="Completed self-assessment of executive thinking, bias, and system health.",
            details={
                "overall_score": report.overall_score,
                "bias_count": len(report.biases),
            },
            succeeded=True,
        )

    def run_prediction(self) -> AutopilotPhaseResult:
        baseline = self.scenario_service.get_simulation_result("baseline")
        recession = self.scenario_service.get_simulation_result("recession")
        if baseline is None or recession is None:
            self.scenario_service.run_all_simulations()
            baseline = baseline or self.scenario_service.get_simulation_result("baseline")
            recession = recession or self.scenario_service.get_simulation_result("recession")

        details = {
            "baseline_scenario": baseline.scenario_type.value if baseline else None,
            "recession_scenario": recession.scenario_type.value if recession else None,
            "baseline_confidence": baseline.confidence if baseline else None,
            "recession_confidence": recession.confidence if recession else None,
        }

        return AutopilotPhaseResult(
            phase=AutopilotCyclePhase.PREDICTION,
            summary="Produced near-term scenario projections for baseline and recession stress tests.",
            details=details,
            succeeded=True,
        )

    def run_comparison(self) -> AutopilotPhaseResult:
        comparison = self.multi_company_service.get_last_comparison()
        if comparison is None:
            companies = self.multi_company_service.list_available_companies()
            if len(companies) >= 2:
                comparison = self.multi_company_service.compare_companies(companies[:2])

        details = {
            "comparison_available": comparison is not None,
            "company_count": len(getattr(comparison, 'companies', [])) if comparison else 0,
        }

        return AutopilotPhaseResult(
            phase=AutopilotCyclePhase.COMPARISON,
            summary="Validated current plans against multi-company competitive benchmarks.",
            details=details,
            succeeded=comparison is not None,
        )

    def run_strategy(self, prediction: AutopilotPhaseResult) -> AutopilotPhaseResult:
        try:
            scenario_type = prediction.details.get("baseline_scenario") if prediction.details else "baseline"
            strategy_report = self.strategy_service.run_strategy_for_scenario_type(scenario_type)
            return AutopilotPhaseResult(
                phase=AutopilotCyclePhase.STRATEGY,
                summary="Generated a recommended strategy bundle based on the latest scenario forecast.",
                details={
                    "strategy_report_id": strategy_report.report_id,
                    "scenario_type": strategy_report.scenario_type.value,
                    "alignment_score": strategy_report.alignment_score,
                },
                succeeded=True,
            )
        except Exception as exc:
            return AutopilotPhaseResult(
                phase=AutopilotCyclePhase.STRATEGY,
                summary=f"Strategy generation failed: {exc}",
                details={"error": str(exc)},
                succeeded=False,
            )

    def run_execution(self, strategy_result: AutopilotPhaseResult) -> AutopilotPhaseResult:
        memory_context = {
            "strategy_report_id": strategy_result.details.get("strategy_report_id") if strategy_result.details else None,
            "scenario_type": strategy_result.details.get("scenario_type") if strategy_result.details else None,
        }
        self.memory_service.add_memory(
            item_type=MemoryItemType.STRATEGY_EXECUTED,
            title="Autopilot strategy execution",
            description=(
                "Enterprise Autopilot recorded strategy action and persisted execution context."
            ),
            context=memory_context,
            importance=MemoryImportance.HIGH,
            tags=["AUTOPILOT", "STRATEGY", "EXECUTION"],
        )
        return AutopilotPhaseResult(
            phase=AutopilotCyclePhase.EXECUTION,
            summary="Committed the chosen strategy bundle into execution memory and persisted decision context.",
            details=memory_context,
            succeeded=True,
        )

    def run_learning(self, cycle: AutopilotCycleResult) -> AutopilotPhaseResult:
        learn = self.learning_service.update_from_cycle(cycle)
        return AutopilotPhaseResult(
            phase=AutopilotCyclePhase.LEARNING,
            summary="Captured learning signals and prepared follow-up guidance for the next cycle.",
            details=learn,
            succeeded=True,
        )

    def _build_cycle_summary(self, cycle: AutopilotCycleResult) -> str:
        successes = [phase.phase.value for phase in cycle.phases if phase.succeeded]
        failures = [phase.phase.value for phase in cycle.phases if not phase.succeeded]
        summary = (
            f"Autopilot cycle completed with {len(successes)} successful phases"
            f" and {len(failures)} failed phases."
        )
        if failures:
            summary += f" Failed phases: {', '.join(failures)}."
        return summary

    def _build_key_actions(self, cycle: AutopilotCycleResult) -> List[str]:
        actions = []
        for phase in cycle.phases:
            if phase.phase == AutopilotCyclePhase.STRATEGY and phase.succeeded:
                report_id = phase.details.get("strategy_report_id") if phase.details else None
                actions.append("Review strategy report {}".format(report_id))
            elif phase.phase == AutopilotCyclePhase.COMPARISON and phase.succeeded:
                actions.append("Validate competitive comparison summaries.")
        if not actions:
            actions.append("Investigate autopilot phase output and system health.")
        return actions

    def _build_experience_notes(self, cycle: AutopilotCycleResult) -> str:
        notes = [
            phase.summary for phase in cycle.phases if phase.succeeded and phase.details
        ]
        return " \n".join(notes)

    def _build_cycle_metrics(self, cycle: AutopilotCycleResult) -> Dict[str, object]:
        return {
            "phase_count": len(cycle.phases),
            "successful_phases": len([p for p in cycle.phases if p.succeeded]),
            "failed_phases": len([p for p in cycle.phases if not p.succeeded]),
        }
