"""
Corporate Consciousness Evolution Model
========================================

Defines data structures for tracking how corporate consciousness evolves over time
in response to external events, internal changes, and strategic transitions.

This module represents Step AF: Scenario-Driven Consciousness Evolution
- Captures evolutionary phases (EMERGING → GROWING → CONSOLIDATING → TRANSFORMING → MATURING)
- Tracks triggers that drive consciousness evolution
- Maintains evolution state with momentum and stability metrics
- Enables temporal analysis of corporate self-awareness development
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ConsciousnessPhase(str, Enum):
    """Phases of corporate consciousness development over time."""
    EMERGING = "EMERGING"  # Initial formation of corporate consciousness
    GROWING = "GROWING"  # Strengthening and developing consciousness
    CONSOLIDATING = "CONSOLIDATING"  # Stabilizing and integrating consciousness
    TRANSFORMING = "TRANSFORMING"  # Major shifts in consciousness
    MATURING = "MATURING"  # Stable, refined consciousness


class EvolutionTriggerType(str, Enum):
    """Types of events that trigger consciousness evolution."""
    EXTERNAL_SHOCK = "EXTERNAL_SHOCK"  # Market crisis, regulation change, competitive disruption
    INTERNAL_MILESTONE = "INTERNAL_MILESTONE"  # Achievement, failure, transformation
    STRATEGY_SHIFT = "STRATEGY_SHIFT"  # Major change in corporate strategy
    CULTURE_SHIFT = "CULTURE_SHIFT"  # Significant cultural transformation
    PERFORMANCE_BREAKPOINT = "PERFORMANCE_BREAKPOINT"  # Crossing key performance thresholds


class ConsciousnessEvolutionEvent(BaseModel):
    """
    Represents a single event that impacts corporate consciousness evolution.
    
    Each event captures:
    - What triggered the evolution (trigger_type)
    - Description of the event
    - Quantified impacts on different consciousness dimensions
    """
    event_id: str = Field(
        ...,
        description="Unique identifier for this evolution event"
    )
    trigger_type: EvolutionTriggerType = Field(
        ...,
        description="Type of trigger causing evolution"
    )
    description: str = Field(
        ...,
        description="Human-readable description of the event"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this event occurred"
    )
    impact_on_identity: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Impact on corporate identity (-1 to 1)"
    )
    impact_on_purpose: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Impact on corporate purpose (-1 to 1)"
    )
    impact_on_direction: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Impact on strategic direction (-1 to 1)"
    )
    impact_on_risk_posture: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Impact on risk posture (-1: more conservative, 1: more aggressive)"
    )
    
    @property
    def total_impact(self) -> float:
        """Calculate total impact magnitude across all dimensions."""
        return abs(self.impact_on_identity) + abs(self.impact_on_purpose) + \
               abs(self.impact_on_direction) + abs(self.impact_on_risk_posture)


class ConsciousnessEvolutionState(BaseModel):
    """
    Represents the current state of corporate consciousness evolution.
    
    Tracks:
    - Current phase in the evolution journey
    - Momentum (speed and direction of change)
    - Stability (consistency and coherence)
    - History of events that led to this state
    """
    current_phase: ConsciousnessPhase = Field(
        default=ConsciousnessPhase.EMERGING,
        description="Current phase in consciousness evolution"
    )
    momentum: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Rate and intensity of consciousness change (0=static, 1=rapidly evolving)"
    )
    stability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Coherence and consistency of consciousness (0=fragmented, 1=highly coherent)"
    )
    last_update: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of last state update"
    )
    history: List[ConsciousnessEvolutionEvent] = Field(
        default_factory=list,
        description="Historical record of events driving evolution"
    )
    
    @property
    def total_events(self) -> int:
        """Count total events in history."""
        return len(self.history)
    
    @property
    def recent_events(self, limit: int = 5) -> List[ConsciousnessEvolutionEvent]:
        """Get recent events (most recent first)."""
        return sorted(self.history, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    @property
    def phase_duration(self) -> Optional[float]:
        """
        Estimate how long the current phase has been active (in days).
        Returns None if insufficient history.
        """
        if not self.history:
            return None
        recent = self.recent_events
        if recent:
            return (datetime.now() - recent[0].timestamp).days
        return None


class ConsciousnessEvolutionTransition(BaseModel):
    """
    Records a transition from one consciousness phase to another.
    """
    from_phase: ConsciousnessPhase = Field(
        ...,
        description="Phase transitioning from"
    )
    to_phase: ConsciousnessPhase = Field(
        ...,
        description="Phase transitioning to"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When transition occurred"
    )
    trigger_event_ids: List[str] = Field(
        default_factory=list,
        description="IDs of events that triggered this transition"
    )
    transition_reason: str = Field(
        ...,
        description="Explanation of why this phase transition occurred"
    )


class ConsciousnessEvolutionMetrics(BaseModel):
    """
    Computed metrics for analyzing consciousness evolution patterns.
    """
    phase_duration_days: float = Field(
        ...,
        description="How long current phase has been active"
    )
    average_event_impact: float = Field(
        ...,
        description="Average total impact of recent events"
    )
    external_shock_frequency: float = Field(
        ...,
        ge=0.0,
        description="Number of external shocks per time period"
    )
    internal_change_frequency: float = Field(
        ...,
        ge=0.0,
        description="Number of internal changes per time period"
    )
    momentum_trajectory: str = Field(
        ...,
        description="Direction of momentum (increasing/decreasing/stable)"
    )
    stability_trajectory: str = Field(
        ...,
        description="Direction of stability (improving/degrading/stable)"
    )


class ConsciousnessEvolutionReport(BaseModel):
    """
    Comprehensive report on consciousness evolution for stakeholder communication.
    """
    period: str = Field(
        ...,
        description="Reporting period"
    )
    current_state: ConsciousnessEvolutionState = Field(
        ...,
        description="Current evolution state"
    )
    metrics: ConsciousnessEvolutionMetrics = Field(
        ...,
        description="Evolution metrics and analysis"
    )
    phase_characteristics: str = Field(
        ...,
        description="Description of current phase characteristics"
    )
    recent_key_events: List[ConsciousnessEvolutionEvent] = Field(
        default_factory=list,
        description="Most impactful recent events"
    )
    momentum_narrative: str = Field(
        ...,
        description="Narrative on momentum and direction of change"
    )
    stability_narrative: str = Field(
        ...,
        description="Narrative on consciousness coherence"
    )
    anticipated_next_phase: ConsciousnessPhase = Field(
        ...,
        description="Predicted next phase if current trajectory continues"
    )
    strategic_implications: List[str] = Field(
        default_factory=list,
        description="Strategic implications of current evolution state"
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Actions recommended to guide consciousness evolution"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="When this report was generated"
    )
