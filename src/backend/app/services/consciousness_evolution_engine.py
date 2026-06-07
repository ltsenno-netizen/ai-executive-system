"""
Consciousness Evolution Engine
===============================

Core logic for simulating and computing how corporate consciousness evolves
in response to external events, internal state changes, and strategic transitions.

This engine implements the 3-step evolution process:
1. extract_evolution_triggers() - Identify events driving evolution
2. update_phase() - Calculate new phase based on impacts
3. apply_evolution_to_consciousness() - Reflect changes in consciousness model
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
import uuid

from ..models.corporate_consciousness_model import (
    CorporateConsciousness,
    IdentityStatement,
    PurposeStatement,
    StrategicDirection,
)
from ..models.corporate_consciousness_evolution_model import (
    ConsciousnessPhase,
    EvolutionTriggerType,
    ConsciousnessEvolutionEvent,
    ConsciousnessEvolutionState,
    ConsciousnessEvolutionTransition,
    ConsciousnessEvolutionMetrics,
    ConsciousnessEvolutionReport,
)


class ConsciousnessEvolutionEngine:
    """
    Engine for computing consciousness evolution based on triggers and impacts.
    """
    
    # Phase transition thresholds
    PHASE_TRANSITION_IMPACT_THRESHOLD = 0.5  # Total impact needed to trigger phase change
    MOMENTUM_HIGH_THRESHOLD = 0.7  # Momentum considered "high"
    MOMENTUM_LOW_THRESHOLD = 0.3  # Momentum considered "low"
    
    # Phase sequences for forward progression
    PHASE_SEQUENCE = [
        ConsciousnessPhase.EMERGING,
        ConsciousnessPhase.GROWING,
        ConsciousnessPhase.CONSOLIDATING,
        ConsciousnessPhase.TRANSFORMING,
        ConsciousnessPhase.MATURING,
    ]
    
    @staticmethod
    def extract_evolution_triggers(
        consciousness: CorporateConsciousness,
        autonomous_cycles: Optional[List[Dict]] = None,
        environment_events: Optional[List[Dict]] = None,
        culture_changes: Optional[Dict] = None,
    ) -> List[ConsciousnessEvolutionEvent]:
        """
        Extract evolution triggers from various data sources.
        
        Analyzes:
        - Autonomous cycle milestones (performance breakpoints)
        - Environment events (external shocks)
        - Culture changes (culture shifts)
        - Internal state changes (strategy shifts)
        
        Args:
            consciousness: Current corporate consciousness
            autonomous_cycles: List of autonomous cycle results
            environment_events: List of environment events
            culture_changes: Culture change metrics
            
        Returns:
            List of ConsciousnessEvolutionEvent objects
        """
        events: List[ConsciousnessEvolutionEvent] = []
        
        # 1. Extract external environment shocks
        if environment_events:
            for env_event in environment_events:
                if isinstance(env_event, dict) and "severity" in env_event:
                    severity = env_event.get("severity", 0.0)
                    if severity > 0.6:  # Only significant events trigger evolution
                        event = ConsciousnessEvolutionEvent(
                            event_id=f"env_{uuid.uuid4().hex[:8]}",
                            trigger_type=EvolutionTriggerType.EXTERNAL_SHOCK,
                            description=env_event.get(
                                "description",
                                "External environment shock detected"
                            ),
                            timestamp=env_event.get("timestamp", datetime.now()),
                            impact_on_direction=severity * 0.8,  # Affects direction most
                            impact_on_risk_posture=severity * 0.6,  # Affects risk posture
                            impact_on_identity=severity * 0.3,  # Some identity impact
                        )
                        events.append(event)
        
        # 2. Extract internal performance breakpoints
        if autonomous_cycles:
            for i, cycle in enumerate(autonomous_cycles[-3:]):  # Last 3 cycles
                if isinstance(cycle, dict):
                    cycle_health = cycle.get("overall_health_score", 0.5)
                    if i == 0:
                        continue  # Skip current cycle
                    
                    # Detect performance jumps
                    prev_health = autonomous_cycles[max(0, i-1)].get(
                        "overall_health_score",
                        0.5
                    ) if isinstance(autonomous_cycles[max(0, i-1)], dict) else 0.5
                    
                    health_change = abs(cycle_health - prev_health)
                    if health_change > 0.3:  # Significant performance change
                        direction = "improvement" if cycle_health > prev_health else "decline"
                        event = ConsciousnessEvolutionEvent(
                            event_id=f"perf_{uuid.uuid4().hex[:8]}",
                            trigger_type=EvolutionTriggerType.PERFORMANCE_BREAKPOINT,
                            description=f"Performance {direction} detected",
                            timestamp=datetime.now(),
                            impact_on_purpose=health_change * 0.7,
                            impact_on_direction=health_change * 0.5,
                        )
                        events.append(event)
        
        # 3. Detect culture shifts
        if culture_changes and isinstance(culture_changes, dict):
            cultural_momentum = culture_changes.get("momentum", 0.0)
            if abs(cultural_momentum) > 0.6:  # Significant cultural shift
                event = ConsciousnessEvolutionEvent(
                    event_id=f"cult_{uuid.uuid4().hex[:8]}",
                    trigger_type=EvolutionTriggerType.CULTURE_SHIFT,
                    description="Significant cultural transformation detected",
                    timestamp=datetime.now(),
                    impact_on_identity=abs(cultural_momentum) * 0.8,
                    impact_on_purpose=abs(cultural_momentum) * 0.6,
                )
                events.append(event)
        
        # 4. Detect strategy shifts
        if consciousness and consciousness.strategic_direction:
            # If risk_posture or major focus areas changed significantly
            event = ConsciousnessEvolutionEvent(
                event_id=f"strat_{uuid.uuid4().hex[:8]}",
                trigger_type=EvolutionTriggerType.STRATEGY_SHIFT,
                description="Strategic direction recalibration",
                timestamp=datetime.now(),
                impact_on_direction=0.5,
                impact_on_risk_posture=0.3,
            )
            # Only add if consciousness shows signs of strategic change
            if consciousness.strategic_direction.innovation_intensity > 0.7:
                events.append(event)
        
        return events
    
    @staticmethod
    def update_phase(
        state: ConsciousnessEvolutionState,
        events: List[ConsciousnessEvolutionEvent],
    ) -> Tuple[ConsciousnessEvolutionState, Optional[ConsciousnessEvolutionTransition]]:
        """
        Update consciousness phase based on recent events.
        
        Phase progression logic:
        - Total impact > THRESHOLD + momentum > 0.5 → move to next phase
        - Multiple external shocks → jump phases
        - Negative impact with low stability → stay/regress
        
        Args:
            state: Current evolution state
            events: Recent triggering events
            
        Returns:
            Tuple of (updated_state, transition or None)
        """
        # Calculate total impact from events
        total_positive_impact = sum(
            max(0, e.impact_on_direction + e.impact_on_identity)
            for e in events
        )
        total_negative_impact = sum(
            max(0, -e.impact_on_direction - e.impact_on_identity)
            for e in events
        )
        net_impact = total_positive_impact - total_negative_impact
        
        # Count event types
        external_shocks = sum(
            1 for e in events
            if e.trigger_type == EvolutionTriggerType.EXTERNAL_SHOCK
        )
        
        # Update momentum (weighted toward recent events)
        event_momentum = abs(net_impact) / max(1, len(events))
        new_momentum = (state.momentum * 0.6) + (event_momentum * 0.4)
        new_momentum = min(1.0, max(0.0, new_momentum))
        
        # Update stability
        # Positive impact increases stability, negative impact decreases it
        impact_on_stability = net_impact * 0.1
        new_stability = state.stability + impact_on_stability
        new_stability = min(1.0, max(0.0, new_stability))
        
        # Determine if phase transition should occur
        transition = None
        new_phase = state.current_phase
        
        if len(events) > 0:
            # Conditions for phase advancement
            should_advance = (
                abs(net_impact) > ConsciousnessEvolutionEngine.PHASE_TRANSITION_IMPACT_THRESHOLD
                and new_momentum > 0.5
                and new_stability > 0.3
            )
            
            # Multiple shocks can cause phase jumps
            if external_shocks >= 2:
                should_advance = True
            
            if should_advance:
                current_idx = ConsciousnessEvolutionEngine.PHASE_SEQUENCE.index(
                    state.current_phase
                )
                
                # Determine how many phases to advance
                phases_to_advance = 1
                if external_shocks >= 2:
                    phases_to_advance = min(2, len(ConsciousnessEvolutionEngine.PHASE_SEQUENCE) - current_idx - 1)
                
                new_idx = min(
                    current_idx + phases_to_advance,
                    len(ConsciousnessEvolutionEngine.PHASE_SEQUENCE) - 1
                )
                new_phase = ConsciousnessEvolutionEngine.PHASE_SEQUENCE[new_idx]
                
                if new_phase != state.current_phase:
                    transition = ConsciousnessEvolutionTransition(
                        from_phase=state.current_phase,
                        to_phase=new_phase,
                        timestamp=datetime.now(),
                        trigger_event_ids=[e.event_id for e in events[:3]],
                        transition_reason=(
                            f"Phase advancement driven by {len(events)} events "
                            f"with net impact {net_impact:.2f}"
                        ),
                    )
        
        # Create updated state
        updated_state = ConsciousnessEvolutionState(
            current_phase=new_phase,
            momentum=new_momentum,
            stability=new_stability,
            last_update=datetime.now(),
            history=state.history + events,
        )
        
        return updated_state, transition
    
    @staticmethod
    def apply_evolution_to_consciousness(
        consciousness: CorporateConsciousness,
        state: ConsciousnessEvolutionState,
        events: List[ConsciousnessEvolutionEvent],
    ) -> CorporateConsciousness:
        """
        Apply evolution state changes back to the consciousness model.
        
        Adjustments based on phase and impacts:
        - TRANSFORMING: Increase innovation_intensity, risk_posture more aggressive
        - CONSOLIDATING: Increase coherence and stability scores
        - MATURING: Focus on long-term value, decrease short-term volatility
        
        Args:
            consciousness: Current consciousness to update
            state: Evolution state with impacts
            events: Triggering events
            
        Returns:
            Updated consciousness model
        """
        # Calculate average impacts from recent events
        avg_identity_impact = (
            sum(e.impact_on_identity for e in events[-5:]) / max(1, len(events[-5:]))
        )
        avg_direction_impact = (
            sum(e.impact_on_direction for e in events[-5:]) / max(1, len(events[-5:]))
        )
        avg_risk_impact = (
            sum(e.impact_on_risk_posture for e in events[-5:]) / max(1, len(events[-5:]))
        )
        
        # Create a copy of consciousness with adjustments
        updated_consciousness = consciousness.copy(deep=True)
        
        # Adjust based on current phase
        if state.current_phase == ConsciousnessPhase.EMERGING:
            # Early stage: focus on establishing identity
            if updated_consciousness.identity:
                updated_consciousness.identity.identity_confidence = max(
                    0.3, updated_consciousness.identity.identity_confidence - 0.1
                )
        
        elif state.current_phase == ConsciousnessPhase.GROWING:
            # Growth stage: increase confidence, explore more
            if updated_consciousness.strategic_direction:
                updated_consciousness.strategic_direction.innovation_intensity = min(
                    0.9, updated_consciousness.strategic_direction.innovation_intensity + 0.1
                )
        
        elif state.current_phase == ConsciousnessPhase.CONSOLIDATING:
            # Consolidation: increase stability and coherence
            updated_consciousness.coherence_score = min(
                1.0, updated_consciousness.coherence_score + 0.1
            )
            if updated_consciousness.strategic_direction:
                updated_consciousness.strategic_direction.innovation_intensity = max(
                    0.3, updated_consciousness.strategic_direction.innovation_intensity - 0.1
                )
        
        elif state.current_phase == ConsciousnessPhase.TRANSFORMING:
            # Transformation: embrace change, increase risk tolerance
            if updated_consciousness.strategic_direction:
                # Shift risk posture based on impacts
                if avg_risk_impact > 0.3:
                    updated_consciousness.strategic_direction.risk_posture = "aggressive"
                    updated_consciousness.strategic_direction.innovation_intensity = min(
                        1.0, updated_consciousness.strategic_direction.innovation_intensity + 0.15
                    )
                else:
                    updated_consciousness.strategic_direction.risk_posture = "balanced"
        
        elif state.current_phase == ConsciousnessPhase.MATURING:
            # Maturity: focus on sustainability, long-term thinking
            if updated_consciousness.strategic_direction:
                updated_consciousness.strategic_direction.risk_posture = "risk-averse"
                updated_consciousness.strategic_direction.innovation_intensity = max(
                    0.4, updated_consciousness.strategic_direction.innovation_intensity - 0.1
                )
            updated_consciousness.coherence_score = min(
                1.0, updated_consciousness.coherence_score + 0.05
            )
        
        # Apply specific impacts from events
        if avg_identity_impact != 0:
            if updated_consciousness.identity:
                updated_consciousness.identity.identity_confidence = max(
                    0.0, min(1.0, updated_consciousness.identity.identity_confidence + avg_identity_impact * 0.2)
                )
        
        # Update overall consciousness metrics based on stability
        updated_consciousness.overall_consciousness_score = (
            updated_consciousness.overall_consciousness_score * 0.7 +
            state.stability * 0.3
        )
        
        # Add phase information to strategic implications if not present
        if not any("phase" in impl.lower() for impl in updated_consciousness.strategic_implications):
            updated_consciousness.strategic_implications.insert(
                0, f"Now in {state.current_phase} phase of consciousness development"
            )
        
        return updated_consciousness
    
    @staticmethod
    def compute_evolution_metrics(
        state: ConsciousnessEvolutionState,
        events: List[ConsciousnessEvolutionEvent],
        period_days: int = 30,
    ) -> ConsciousnessEvolutionMetrics:
        """
        Compute evolution metrics for analysis and reporting.
        
        Args:
            state: Current evolution state
            events: All events in period
            period_days: Number of days in analysis period
            
        Returns:
            ConsciousnessEvolutionMetrics object
        """
        # Phase duration
        phase_start = min((e.timestamp for e in events if e.trigger_type), default=datetime.now())
        phase_duration = (datetime.now() - phase_start).days if events else 0
        
        # Average event impact
        avg_impact = (
            sum(e.total_impact for e in events) / len(events) if events else 0.0
        )
        
        # Event frequencies
        recent_events = [e for e in events if (datetime.now() - e.timestamp).days <= period_days]
        external_shocks = sum(
            1 for e in recent_events
            if e.trigger_type == EvolutionTriggerType.EXTERNAL_SHOCK
        )
        internal_changes = sum(
            1 for e in recent_events
            if e.trigger_type in [
                EvolutionTriggerType.INTERNAL_MILESTONE,
                EvolutionTriggerType.CULTURE_SHIFT,
                EvolutionTriggerType.STRATEGY_SHIFT,
            ]
        )
        
        # Trajectory calculation
        if len(recent_events) > 1:
            recent_momentum_trend = (state.momentum - 0.5) * 2  # Normalized
            momentum_trajectory = (
                "increasing" if recent_momentum_trend > 0.1 else
                "decreasing" if recent_momentum_trend < -0.1 else
                "stable"
            )
            
            stability_trend = (state.stability - 0.5) * 2
            stability_trajectory = (
                "improving" if stability_trend > 0.1 else
                "degrading" if stability_trend < -0.1 else
                "stable"
            )
        else:
            momentum_trajectory = "stable"
            stability_trajectory = "stable"
        
        return ConsciousnessEvolutionMetrics(
            phase_duration_days=float(phase_duration),
            average_event_impact=avg_impact,
            external_shock_frequency=external_shocks / max(1, period_days / 30),
            internal_change_frequency=internal_changes / max(1, period_days / 30),
            momentum_trajectory=momentum_trajectory,
            stability_trajectory=stability_trajectory,
        )
    
    @staticmethod
    def predict_next_phase(
        state: ConsciousnessEvolutionState,
        momentum: float,
    ) -> ConsciousnessPhase:
        """
        Predict the next consciousness phase based on current state.
        
        Args:
            state: Current evolution state
            momentum: Current momentum level (0-1)
            
        Returns:
            Predicted next ConsciousnessPhase
        """
        current_idx = ConsciousnessEvolutionEngine.PHASE_SEQUENCE.index(state.current_phase)
        
        if momentum > 0.7 and current_idx < len(ConsciousnessEvolutionEngine.PHASE_SEQUENCE) - 1:
            return ConsciousnessEvolutionEngine.PHASE_SEQUENCE[current_idx + 1]
        
        return state.current_phase
