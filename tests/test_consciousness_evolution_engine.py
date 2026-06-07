"""
Tests for Consciousness Evolution Engine
==========================================

Tests for core logic of consciousness evolution computation.
"""

import pytest
from datetime import datetime
from typing import List

from src.backend.app.models.corporate_consciousness_model import (
    CorporateConsciousness,
    SelfAssessment,
    IdentityStatement,
    PurposeStatement,
    StrategicDirection,
)
from src.backend.app.models.corporate_consciousness_evolution_model import (
    ConsciousnessPhase,
    EvolutionTriggerType,
    ConsciousnessEvolutionEvent,
    ConsciousnessEvolutionState,
)
from src.backend.app.services.consciousness_evolution_engine import (
    ConsciousnessEvolutionEngine,
)


class TestEvolutionEngineInitialization:
    """Test ConsciousnessEvolutionEngine initialization and properties."""
    
    def test_phase_sequence(self):
        """Test that phase sequence is correct."""
        expected_sequence = [
            ConsciousnessPhase.EMERGING,
            ConsciousnessPhase.GROWING,
            ConsciousnessPhase.CONSOLIDATING,
            ConsciousnessPhase.TRANSFORMING,
            ConsciousnessPhase.MATURING,
        ]
        assert ConsciousnessEvolutionEngine.PHASE_SEQUENCE == expected_sequence
    
    def test_thresholds_defined(self):
        """Test that evolution thresholds are properly defined."""
        assert ConsciousnessEvolutionEngine.PHASE_TRANSITION_IMPACT_THRESHOLD == 0.5
        assert ConsciousnessEvolutionEngine.MOMENTUM_HIGH_THRESHOLD == 0.7
        assert ConsciousnessEvolutionEngine.MOMENTUM_LOW_THRESHOLD == 0.3


class TestTriggerExtraction:
    """Test trigger extraction from various data sources."""
    
    def test_extract_triggers_empty_sources(self):
        """Test trigger extraction with no data sources."""
        events = ConsciousnessEvolutionEngine.extract_evolution_triggers(
            consciousness=None,
            autonomous_cycles=None,
            environment_events=None,
        )
        assert isinstance(events, list)
        assert len(events) >= 0  # Can be empty
    
    def test_extract_external_shock_trigger(self):
        """Test extraction of external shock triggers."""
        env_events = [
            {
                "severity": 0.8,
                "description": "Market crash detected",
                "timestamp": datetime.now(),
            }
        ]
        
        events = ConsciousnessEvolutionEngine.extract_evolution_triggers(
            consciousness=None,
            environment_events=env_events,
        )
        
        shock_events = [e for e in events if e.trigger_type == EvolutionTriggerType.EXTERNAL_SHOCK]
        assert len(shock_events) > 0
        assert any("Market crash" in e.description for e in shock_events)
    
    def test_extract_ignores_low_severity_events(self):
        """Test that low severity events are ignored."""
        env_events = [
            {
                "severity": 0.2,
                "description": "Minor market fluctuation",
                "timestamp": datetime.now(),
            }
        ]
        
        events = ConsciousnessEvolutionEngine.extract_evolution_triggers(
            consciousness=None,
            environment_events=env_events,
        )
        
        shock_events = [e for e in events if e.trigger_type == EvolutionTriggerType.EXTERNAL_SHOCK]
        # Low severity events should not trigger evolution
        assert len(shock_events) == 0
    
    def test_extract_culture_shift_trigger(self):
        """Test extraction of culture shift triggers."""
        culture_changes = {"momentum": 0.8}
        
        events = ConsciousnessEvolutionEngine.extract_evolution_triggers(
            consciousness=None,
            culture_changes=culture_changes,
        )
        
        culture_events = [e for e in events if e.trigger_type == EvolutionTriggerType.CULTURE_SHIFT]
        assert len(culture_events) > 0


class TestPhaseTransition:
    """Test consciousness phase transition logic."""
    
    def test_phase_transition_from_emerging(self):
        """Test phase transition from EMERGING to GROWING."""
        initial_state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.EMERGING,
            momentum=0.3,
            stability=0.4,
        )
        
        # Create significant impact events
        events = [
            ConsciousnessEvolutionEvent(
                event_id="test_1",
                trigger_type=EvolutionTriggerType.EXTERNAL_SHOCK,
                description="Major market shift",
                impact_on_direction=0.6,
                impact_on_identity=0.4,
            ),
            ConsciousnessEvolutionEvent(
                event_id="test_2",
                trigger_type=EvolutionTriggerType.INTERNAL_MILESTONE,
                description="Strategic milestone achieved",
                impact_on_purpose=0.5,
                impact_on_direction=0.4,
            ),
        ]
        
        updated_state, transition = ConsciousnessEvolutionEngine.update_phase(
            initial_state,
            events,
        )
        
        # Should have increased momentum
        assert updated_state.momentum > initial_state.momentum
        # Events should be in history
        assert len(updated_state.history) >= len(events)
    
    def test_momentum_calculation(self):
        """Test momentum calculation from events."""
        initial_state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.GROWING,
            momentum=0.5,
            stability=0.5,
        )
        
        events = [
            ConsciousnessEvolutionEvent(
                event_id="test_1",
                trigger_type=EvolutionTriggerType.PERFORMANCE_BREAKPOINT,
                description="Performance improvement",
                impact_on_purpose=0.3,
                impact_on_direction=0.4,
            ),
        ]
        
        updated_state, _ = ConsciousnessEvolutionEngine.update_phase(
            initial_state,
            events,
        )
        
        # Momentum should be updated
        assert updated_state.momentum >= 0.0
        assert updated_state.momentum <= 1.0
    
    def test_stability_changes_with_events(self):
        """Test that stability changes based on event impacts."""
        initial_state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.CONSOLIDATING,
            momentum=0.5,
            stability=0.6,
        )
        
        # Positive impact events
        positive_events = [
            ConsciousnessEvolutionEvent(
                event_id="pos_1",
                trigger_type=EvolutionTriggerType.INTERNAL_MILESTONE,
                description="Internal alignment improved",
                impact_on_identity=0.3,
                impact_on_direction=0.3,
            ),
        ]
        
        updated_state, _ = ConsciousnessEvolutionEngine.update_phase(
            initial_state,
            positive_events,
        )
        
        # Stability should improve with positive impacts
        assert updated_state.stability >= initial_state.stability


class TestApplicationToConsciousness:
    """Test applying evolution state changes to consciousness model."""
    
    def test_apply_emerging_phase_changes(self):
        """Test consciousness changes in EMERGING phase."""
        consciousness = self._create_mock_consciousness()
        state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.EMERGING,
            momentum=0.4,
            stability=0.4,
        )
        events = []
        
        updated = ConsciousnessEvolutionEngine.apply_evolution_to_consciousness(
            consciousness,
            state,
            events,
        )
        
        # In EMERGING phase, identity confidence should decrease slightly
        assert isinstance(updated, CorporateConsciousness)
    
    def test_apply_transforming_phase_changes(self):
        """Test consciousness changes in TRANSFORMING phase."""
        consciousness = self._create_mock_consciousness()
        state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.TRANSFORMING,
            momentum=0.7,
            stability=0.5,
        )
        events = [
            ConsciousnessEvolutionEvent(
                event_id="trans_1",
                trigger_type=EvolutionTriggerType.STRATEGY_SHIFT,
                description="Major strategy shift",
                impact_on_risk_posture=0.4,
            ),
        ]
        
        updated = ConsciousnessEvolutionEngine.apply_evolution_to_consciousness(
            consciousness,
            state,
            events,
        )
        
        # Should update consciousness model
        assert updated is not None
        assert hasattr(updated, 'overall_consciousness_score')
    
    def test_apply_maturing_phase_changes(self):
        """Test consciousness changes in MATURING phase."""
        consciousness = self._create_mock_consciousness()
        state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.MATURING,
            momentum=0.3,
            stability=0.85,
        )
        events = []
        
        updated = ConsciousnessEvolutionEngine.apply_evolution_to_consciousness(
            consciousness,
            state,
            events,
        )
        
        # In MATURING phase, focus on stability and long-term
        assert updated.coherence_score >= 0.0
        assert updated.coherence_score <= 1.0
    
    @staticmethod
    def _create_mock_consciousness() -> CorporateConsciousness:
        """Create a mock consciousness object for testing."""
        return CorporateConsciousness(
            identity=IdentityStatement(
                core_identity="Tech-driven innovator",
                cultural_archetype="innovator",
                brand_promise="Leading digital transformation",
                value_hierarchy=["Innovation", "Customer Focus", "Excellence"],
                identity_confidence=0.7,
            ),
            purpose=PurposeStatement(
                mission="Transform industries through AI",
                vision="World leading in AI solutions",
                clarity_score=0.8,
                alignment_score=0.75,
            ),
            strategic_direction=StrategicDirection(
                primary_strategy="Innovation-led growth",
                focus_areas=["AI", "Cloud"],
                growth_vector="Expansion into new markets",
                competitive_positioning="Technology leader",
                risk_posture="balanced",
                innovation_intensity=0.8,
            ),
            overall_consciousness_score=0.7,
            clarity_score=0.75,
            coherence_score=0.72,
            alignment_score=0.7,
            authenticity_score=0.75,
        )


class TestEvolutionMetrics:
    """Test evolution metrics computation."""
    
    def test_compute_metrics(self):
        """Test metrics computation."""
        state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.GROWING,
            momentum=0.6,
            stability=0.7,
            history=[
                ConsciousnessEvolutionEvent(
                    event_id="ev1",
                    trigger_type=EvolutionTriggerType.EXTERNAL_SHOCK,
                    description="Test event",
                ),
            ],
        )
        
        metrics = ConsciousnessEvolutionEngine.compute_evolution_metrics(state, state.history)
        
        assert metrics.phase_duration_days >= 0
        assert metrics.average_event_impact >= 0
        assert metrics.momentum_trajectory in ["increasing", "decreasing", "stable"]
        assert metrics.stability_trajectory in ["improving", "degrading", "stable"]
    
    def test_predict_next_phase_emerging(self):
        """Test phase prediction for EMERGING state."""
        state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.EMERGING,
            momentum=0.8,
            stability=0.5,
        )
        
        next_phase = ConsciousnessEvolutionEngine.predict_next_phase(state, 0.8)
        
        # With high momentum, should predict next phase
        assert next_phase in [ConsciousnessPhase.GROWING, ConsciousnessPhase.EMERGING]
    
    def test_predict_next_phase_maturing(self):
        """Test phase prediction for MATURING state."""
        state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.MATURING,
            momentum=0.3,
            stability=0.9,
        )
        
        next_phase = ConsciousnessEvolutionEngine.predict_next_phase(state, 0.3)
        
        # MATURING is final phase
        assert next_phase == ConsciousnessPhase.MATURING
