"""
Corporate Consciousness Evolution Service
==========================================

Service layer for managing consciousness evolution lifecycle.

Responsibilities:
- Load/save evolution state from/to persistent storage
- Orchestrate evolution cycles (extract triggers → update phase → apply changes)
- Integrate with upstream services (Consciousness, Autonomous, Environment, Culture)
- Manage history and reporting
"""

import json
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from ..models.corporate_consciousness_model import CorporateConsciousness
from ..models.corporate_consciousness_evolution_model import (
    ConsciousnessEvolutionState,
    ConsciousnessEvolutionEvent,
    ConsciousnessEvolutionMetrics,
    ConsciousnessEvolutionReport,
    ConsciousnessPhase,
)
from .consciousness_evolution_engine import ConsciousnessEvolutionEngine


class CorporateConsciousnessEvolutionService:
    """
    Service for managing corporate consciousness evolution.
    """
    
    # Data storage paths
    DATA_DIR = Path("data/consciousness/evolution")
    STATE_FILE = DATA_DIR / "evolution_state.json"
    HISTORY_DIR = DATA_DIR / "history"
    
    def __init__(self):
        """Initialize evolution service and ensure storage directories exist."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        self._state_cache: Optional[ConsciousnessEvolutionState] = None
    
    def get_state(self) -> ConsciousnessEvolutionState:
        """
        Retrieve current evolution state from cache or persistent storage.
        
        If no state file exists, initializes with default EMERGING phase.
        
        Returns:
            ConsciousnessEvolutionState object
        """
        # Return from cache if available
        if self._state_cache is not None:
            return self._state_cache
        
        # Try to load from file
        if self.STATE_FILE.exists():
            try:
                with open(self.STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    state = self._deserialize_state(data)
                    self._state_cache = state
                    return state
            except Exception as e:
                print(f"Error loading evolution state: {e}")
        
        # Initialize default state if no file exists
        default_state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.EMERGING,
            momentum=0.3,
            stability=0.5,
            history=[],
        )
        self._state_cache = default_state
        return default_state
    
    def save_state(self, state: ConsciousnessEvolutionState) -> None:
        """
        Save evolution state to persistent storage.
        
        Args:
            state: ConsciousnessEvolutionState to save
        """
        try:
            self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._serialize_state(state), f, indent=2, default=str)
            
            self._state_cache = state
        except Exception as e:
            print(f"Error saving evolution state: {e}")
    
    def run_evolution_cycle(
        self,
        current_consciousness: Optional[CorporateConsciousness] = None,
        autonomous_cycles: Optional[List[Dict[str, Any]]] = None,
        environment_events: Optional[List[Dict[str, Any]]] = None,
        culture_changes: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ConsciousnessEvolutionState, CorporateConsciousness, List[ConsciousnessEvolutionEvent]]:
        """
        Run one complete evolution cycle.
        
        Steps:
        1. Extract evolution triggers from various data sources
        2. Update evolution state (phase, momentum, stability)
        3. Apply evolution to consciousness model
        4. Persist state
        5. Log history
        
        Args:
            current_consciousness: Current corporate consciousness state
            autonomous_cycles: List of autonomous cycle results
            environment_events: List of environment events
            culture_changes: Culture change metrics
            
        Returns:
            Tuple of (updated_state, updated_consciousness, events)
        """
        # Get current state
        current_state = self.get_state()
        
        # Step 1: Extract triggers
        events = ConsciousnessEvolutionEngine.extract_evolution_triggers(
            consciousness=current_consciousness,
            autonomous_cycles=autonomous_cycles,
            environment_events=environment_events,
            culture_changes=culture_changes,
        )
        
        # Step 2: Update phase and state
        updated_state, transition = ConsciousnessEvolutionEngine.update_phase(
            current_state,
            events,
        )
        
        # Step 3: Apply evolution to consciousness
        updated_consciousness = current_consciousness
        if current_consciousness:
            updated_consciousness = ConsciousnessEvolutionEngine.apply_evolution_to_consciousness(
                current_consciousness,
                updated_state,
                events,
            )
        
        # Step 4: Save state
        self.save_state(updated_state)
        
        # Step 5: Log history
        self._log_evolution_cycle(updated_state, events, transition)
        
        return updated_state, updated_consciousness, events
    
    def get_evolution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve historical evolution records.
        
        Args:
            limit: Maximum number of history records to return
            
        Returns:
            List of evolution history dictionaries
        """
        history_files = sorted(
            self.HISTORY_DIR.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]
        
        history = []
        for file in history_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    history.append(json.load(f))
            except Exception as e:
                print(f"Error reading history file {file}: {e}")
        
        return history
    
    def get_evolution_metrics(
        self,
        state: Optional[ConsciousnessEvolutionState] = None,
        period_days: int = 30,
    ) -> ConsciousnessEvolutionMetrics:
        """
        Compute evolution metrics for analysis.
        
        Args:
            state: Evolution state (uses current if None)
            period_days: Period to analyze
            
        Returns:
            ConsciousnessEvolutionMetrics object
        """
        if state is None:
            state = self.get_state()
        
        # Filter events in period
        cutoff = datetime.now() - __import__('datetime').timedelta(days=period_days)
        recent_events = [e for e in state.history if e.timestamp >= cutoff]
        
        return ConsciousnessEvolutionEngine.compute_evolution_metrics(
            state,
            recent_events,
            period_days,
        )
    
    def generate_evolution_report(
        self,
        consciousness: Optional[CorporateConsciousness] = None,
        period: str = "current",
        state: Optional[ConsciousnessEvolutionState] = None,
    ) -> ConsciousnessEvolutionReport:
        """
        Generate comprehensive evolution report.
        
        Args:
            consciousness: Current consciousness (optional)
            period: Reporting period
            state: Evolution state (uses current if None)
            
        Returns:
            ConsciousnessEvolutionReport object
        """
        if state is None:
            state = self.get_state()
        
        metrics = self.get_evolution_metrics(state)
        
        # Get recent key events
        recent_events = sorted(
            state.history[-10:],
            key=lambda e: e.total_impact,
            reverse=True
        )[:5]
        
        # Generate phase characteristics
        phase_characteristics = self._get_phase_characteristics(state.current_phase)
        
        # Generate momentum narrative
        momentum_narrative = self._generate_momentum_narrative(state, metrics)
        
        # Generate stability narrative
        stability_narrative = self._generate_stability_narrative(state, metrics)
        
        # Predict next phase
        anticipated_next = ConsciousnessEvolutionEngine.predict_next_phase(
            state,
            state.momentum,
        )
        
        # Strategic implications
        strategic_implications = self._derive_strategic_implications(
            state,
            metrics,
            recent_events,
        )
        
        # Recommended actions
        recommended_actions = self._derive_recommended_actions(
            state,
            metrics,
            consciousness,
        )
        
        return ConsciousnessEvolutionReport(
            period=period,
            current_state=state,
            metrics=metrics,
            phase_characteristics=phase_characteristics,
            recent_key_events=recent_events,
            momentum_narrative=momentum_narrative,
            stability_narrative=stability_narrative,
            anticipated_next_phase=anticipated_next,
            strategic_implications=strategic_implications,
            recommended_actions=recommended_actions,
        )
    
    def export_evolution_markdown(
        self,
        report: ConsciousnessEvolutionReport,
    ) -> str:
        """
        Export evolution report as formatted Markdown.
        
        Args:
            report: ConsciousnessEvolutionReport to export
            
        Returns:
            Markdown string
        """
        md = []
        
        md.append("# Corporate Consciousness Evolution Report")
        md.append(f"**Period:** {report.period}")
        md.append(f"**Generated:** {report.generated_at.isoformat()}")
        md.append("")
        
        # Executive summary
        md.append("## Executive Summary")
        md.append("")
        md.append(f"The enterprise is currently in the **{report.current_state.current_phase}** phase "
                  f"of consciousness development. Momentum is at {report.current_state.momentum:.0%} "
                  f"and stability at {report.current_state.stability:.0%}.")
        md.append("")
        
        # Current phase
        md.append("## Current Phase: " + report.current_state.current_phase)
        md.append("")
        md.append(report.phase_characteristics)
        md.append("")
        
        # Key metrics
        md.append("## Evolution Metrics")
        md.append("")
        md.append(f"- **Momentum:** {report.current_state.momentum:.0%}")
        md.append(f"- **Stability:** {report.current_state.stability:.0%}")
        md.append(f"- **Phase Duration:** {report.metrics.phase_duration_days:.0f} days")
        md.append(f"- **Average Event Impact:** {report.metrics.average_event_impact:.2f}")
        md.append(f"- **External Shocks:** {report.metrics.external_shock_frequency:.1f}/month")
        md.append(f"- **Internal Changes:** {report.metrics.internal_change_frequency:.1f}/month")
        md.append("")
        
        # Momentum analysis
        md.append("## Momentum & Direction")
        md.append("")
        md.append(report.momentum_narrative)
        md.append(f"- **Trajectory:** {report.metrics.momentum_trajectory.upper()}")
        md.append("")
        
        # Stability analysis
        md.append("## Stability & Coherence")
        md.append("")
        md.append(report.stability_narrative)
        md.append(f"- **Trajectory:** {report.metrics.stability_trajectory.upper()}")
        md.append("")
        
        # Recent events
        md.append("## Recent Key Events")
        md.append("")
        for event in report.recent_key_events:
            md.append(f"- **{event.timestamp.strftime('%Y-%m-%d')}:** {event.description}")
            md.append(f"  - Type: {event.trigger_type.value}")
            md.append(f"  - Impact: {event.total_impact:.2f}")
        md.append("")
        
        # Anticipated next phase
        md.append("## Anticipated Evolution")
        md.append("")
        md.append(f"Based on current momentum and stability trends, the enterprise is anticipated "
                  f"to transition to the **{report.anticipated_next_phase}** phase.")
        md.append("")
        
        # Strategic implications
        md.append("## Strategic Implications")
        md.append("")
        for i, implication in enumerate(report.strategic_implications, 1):
            md.append(f"{i}. {implication}")
        md.append("")
        
        # Recommended actions
        md.append("## Recommended Actions")
        md.append("")
        for i, action in enumerate(report.recommended_actions, 1):
            md.append(f"{i}. {action}")
        md.append("")
        
        return "\n".join(md)
    
    # ========== Private helper methods ==========
    
    @staticmethod
    def _serialize_state(state: ConsciousnessEvolutionState) -> Dict[str, Any]:
        """Serialize evolution state to JSON-compatible dict."""
        return {
            "current_phase": state.current_phase.value,
            "momentum": state.momentum,
            "stability": state.stability,
            "last_update": state.last_update.isoformat(),
            "history": [
                {
                    "event_id": e.event_id,
                    "trigger_type": e.trigger_type.value,
                    "description": e.description,
                    "timestamp": e.timestamp.isoformat(),
                    "impact_on_identity": e.impact_on_identity,
                    "impact_on_purpose": e.impact_on_purpose,
                    "impact_on_direction": e.impact_on_direction,
                    "impact_on_risk_posture": e.impact_on_risk_posture,
                }
                for e in state.history
            ]
        }
    
    @staticmethod
    def _deserialize_state(data: Dict[str, Any]) -> ConsciousnessEvolutionState:
        """Deserialize evolution state from JSON-compatible dict."""
        events = [
            ConsciousnessEvolutionEvent(
                event_id=e["event_id"],
                trigger_type=e["trigger_type"],
                description=e["description"],
                timestamp=datetime.fromisoformat(e["timestamp"]),
                impact_on_identity=e.get("impact_on_identity", 0.0),
                impact_on_purpose=e.get("impact_on_purpose", 0.0),
                impact_on_direction=e.get("impact_on_direction", 0.0),
                impact_on_risk_posture=e.get("impact_on_risk_posture", 0.0),
            )
            for e in data.get("history", [])
        ]
        
        return ConsciousnessEvolutionState(
            current_phase=data["current_phase"],
            momentum=data["momentum"],
            stability=data["stability"],
            last_update=datetime.fromisoformat(data["last_update"]),
            history=events,
        )
    
    def _log_evolution_cycle(
        self,
        state: ConsciousnessEvolutionState,
        events: List[ConsciousnessEvolutionEvent],
        transition: Optional[Any],
    ) -> None:
        """Log evolution cycle to history."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = self.HISTORY_DIR / f"evolution_{timestamp}.json"
            
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "phase": state.current_phase.value,
                "momentum": state.momentum,
                "stability": state.stability,
                "events_count": len(events),
                "transition": transition.model_dump() if transition else None,
            }
            
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error logging evolution cycle: {e}")
    
    @staticmethod
    def _get_phase_characteristics(phase: ConsciousnessPhase) -> str:
        """Get description of phase characteristics."""
        characteristics = {
            ConsciousnessPhase.EMERGING: (
                "The enterprise is in the early stages of consciousness development. Identity is still "
                "forming, purpose is exploratory, and the organization is testing different strategic directions. "
                "High levels of experimentation and low stability are expected as the consciousness solidifies."
            ),
            ConsciousnessPhase.GROWING: (
                "The enterprise is actively developing its consciousness. Identity is becoming clearer, "
                "purpose is solidifying, and strategic direction is gaining focus. Momentum is building as "
                "the organization learns what it stands for and where it wants to go."
            ),
            ConsciousnessPhase.CONSOLIDATING: (
                "The enterprise is consolidating its consciousness into a stable, coherent model. "
                "Identity is well-established, purpose is clear, and strategy is consistent. "
                "The organization is integrating learning and preparing for sustainable growth."
            ),
            ConsciousnessPhase.TRANSFORMING: (
                "The enterprise is undergoing significant transformation in its consciousness. "
                "Major shifts are occurring in identity, purpose, or strategic direction in response to "
                "market changes, leadership evolution, or strategic pivots. This phase involves high change energy."
            ),
            ConsciousnessPhase.MATURING: (
                "The enterprise has reached mature consciousness. Identity is deeply understood, "
                "purpose is compelling and enduring, and strategy reflects deep organizational wisdom. "
                "The consciousness is resilient, adaptable, and oriented toward long-term value creation."
            ),
        }
        return characteristics.get(phase, "Unknown phase characteristics")
    
    @staticmethod
    def _generate_momentum_narrative(
        state: ConsciousnessEvolutionState,
        metrics: ConsciousnessEvolutionMetrics,
    ) -> str:
        """Generate narrative on consciousness momentum."""
        if metrics.momentum_trajectory == "increasing":
            return (
                f"The enterprise consciousness is accelerating its evolution with momentum at {state.momentum:.0%}. "
                f"Recent events and internal dynamics are driving rapid change in consciousness. "
                f"External shocks ({metrics.external_shock_frequency:.1f}/month) and internal changes "
                f"({metrics.internal_change_frequency:.1f}/month) are creating strong evolutionary pressure."
            )
        elif metrics.momentum_trajectory == "decreasing":
            return (
                f"The consciousness evolution has slowed with momentum at {state.momentum:.0%}. "
                f"The organization may be consolidating previous changes or facing external constraints. "
                f"Current event frequency is below historical levels, suggesting a plateau or integration period."
            )
        else:
            return (
                f"The consciousness evolution is stable with momentum maintained at {state.momentum:.0%}. "
                f"The organization is moving at a steady pace, with balanced levels of internal reflection "
                f"and external responsiveness."
            )
    
    @staticmethod
    def _generate_stability_narrative(
        state: ConsciousnessEvolutionState,
        metrics: ConsciousnessEvolutionMetrics,
    ) -> str:
        """Generate narrative on consciousness stability."""
        if metrics.stability_trajectory == "improving":
            return (
                f"Consciousness stability is strengthening at {state.stability:.0%}. "
                f"The organization is achieving greater coherence in identity, purpose, and direction. "
                f"Integration of previous changes is progressing well, creating a more resilient consciousness."
            )
        elif metrics.stability_trajectory == "degrading":
            return (
                f"Consciousness stability is being tested at {state.stability:.0%}. "
                f"Multiple competing influences or recent disruptions may be fragmenting organizational coherence. "
                f"The organization should focus on integrating divergent voices and clarifying core values."
            )
        else:
            return (
                f"Consciousness stability is holding steady at {state.stability:.0%}. "
                f"The organization maintains coherence while navigating change. "
                f"Identity, purpose, and direction remain relatively aligned despite pressures."
            )
    
    @staticmethod
    def _derive_strategic_implications(
        state: ConsciousnessEvolutionState,
        metrics: ConsciousnessEvolutionMetrics,
        events: List[ConsciousnessEvolutionEvent],
    ) -> List[str]:
        """Derive strategic implications from evolution state."""
        implications = []
        
        # Phase implications
        phase_implications = {
            ConsciousnessPhase.EMERGING: "Establish and communicate clear organizational identity",
            ConsciousnessPhase.GROWING: "Scale consciousness communication to all stakeholders",
            ConsciousnessPhase.CONSOLIDATING: "Operationalize consciousness into decision-making",
            ConsciousnessPhase.TRANSFORMING: "Manage transformation carefully to maintain stakeholder trust",
            ConsciousnessPhase.MATURING: "Leverage mature consciousness for strategic advantage",
        }
        implications.append(phase_implications.get(state.current_phase, "Continue evolution journey"))
        
        # Momentum implications
        if metrics.momentum_trajectory == "increasing":
            implications.append("Prepare organization for rapid consciousness transformation")
        elif metrics.momentum_trajectory == "decreasing":
            implications.append("Reflect on learning from recent evolution cycle")
        
        # Stability implications
        if state.stability < 0.4:
            implications.append("Prioritize internal alignment and coherence building")
        elif state.stability > 0.8:
            implications.append("Leverage high coherence for ambitious strategic initiatives")
        
        # Event-based implications
        if metrics.external_shock_frequency > 2:
            implications.append("Build organizational resilience to external disruptions")
        
        return implications
    
    @staticmethod
    def _derive_recommended_actions(
        state: ConsciousnessEvolutionState,
        metrics: ConsciousnessEvolutionMetrics,
        consciousness: Optional[CorporateConsciousness],
    ) -> List[str]:
        """Derive recommended actions based on evolution state."""
        actions = []
        
        # Phase-based actions
        if state.current_phase == ConsciousnessPhase.EMERGING:
            actions.append("Facilitate workshops to clarify identity and purpose with leadership")
            actions.append("Begin communicating emerging consciousness to broader organization")
        elif state.current_phase == ConsciousnessPhase.GROWING:
            actions.append("Expand consciousness development across functional areas")
            actions.append("Create feedback mechanisms to refine consciousness model")
        elif state.current_phase == ConsciousnessPhase.CONSOLIDATING:
            actions.append("Embed consciousness into strategic planning and budgeting processes")
            actions.append("Train managers on consciousness-aligned decision making")
        elif state.current_phase == ConsciousnessPhase.TRANSFORMING:
            actions.append("Manage organizational change carefully to prevent fragmentation")
            actions.append("Communicate transformation journey to stakeholders transparently")
        elif state.current_phase == ConsciousnessPhase.MATURING:
            actions.append("Use consciousness as strategic differentiation")
            actions.append("Mentor other organizations in consciousness development")
        
        # Momentum-based actions
        if metrics.momentum_trajectory == "increasing":
            actions.append("Establish change management infrastructure to guide evolution")
        elif metrics.momentum_trajectory == "decreasing":
            actions.append("Identify and address blockers to consciousness evolution")
        
        # Stability-based actions
        if state.stability < 0.5:
            actions.append("Conduct stakeholder alignment sessions across organization")
        
        return actions[:5]  # Return top 5 actions
