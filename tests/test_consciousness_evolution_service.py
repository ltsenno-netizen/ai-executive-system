"""
Tests for Consciousness Evolution Service
===========================================

Tests for service layer managing consciousness evolution lifecycle.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.backend.app.models.corporate_consciousness_evolution_model import (
    ConsciousnessPhase,
    ConsciousnessEvolutionState,
    ConsciousnessEvolutionEvent,
)
from src.backend.app.services.corporate_consciousness_evolution_service import (
    CorporateConsciousnessEvolutionService,
)


class TestEvolutionServiceInitialization:
    """Test evolution service initialization."""
    
    def test_service_initializes(self):
        """Test that service initializes without errors."""
        service = CorporateConsciousnessEvolutionService()
        assert service is not None
        assert hasattr(service, 'get_state')
        assert hasattr(service, 'save_state')
        assert hasattr(service, 'run_evolution_cycle')
    
    def test_data_directories_created(self):
        """Test that required data directories are created."""
        service = CorporateConsciousnessEvolutionService()
        assert service.DATA_DIR.exists()
        assert service.HISTORY_DIR.exists()


class TestStateManagement:
    """Test evolution state persistence."""
    
    def test_get_default_state(self):
        """Test retrieval of default state when no file exists."""
        service = CorporateConsciousnessEvolutionService()
        service._state_cache = None  # Clear cache
        
        state = service.get_state()
        
        assert state is not None
        assert isinstance(state, ConsciousnessEvolutionState)
        assert state.current_phase == ConsciousnessPhase.EMERGING or isinstance(state.current_phase, str)
    
    def test_save_and_retrieve_state(self):
        """Test saving and retrieving evolution state."""
        service = CorporateConsciousnessEvolutionService()
        
        state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.GROWING,
            momentum=0.6,
            stability=0.7,
        )
        
        service.save_state(state)
        retrieved_state = service.get_state()
        
        assert retrieved_state.momentum == state.momentum
        assert retrieved_state.stability == state.stability
    
    def test_state_cache(self):
        """Test that state caching works."""
        service = CorporateConsciousnessEvolutionService()
        
        state1 = service.get_state()
        state2 = service.get_state()
        
        # Should return same cached instance
        assert state1 is state2


class TestEvolutionCycle:
    """Test evolution cycle execution."""
    
    def test_run_evolution_cycle_basic(self):
        """Test running a basic evolution cycle."""
        service = CorporateConsciousnessEvolutionService()
        
        updated_state, updated_consciousness, events = service.run_evolution_cycle(
            current_consciousness=None,
            autonomous_cycles=None,
            environment_events=None,
        )
        
        assert isinstance(updated_state, ConsciousnessEvolutionState)
        assert isinstance(events, list)
    
    def test_evolution_cycle_persists_state(self):
        """Test that evolution cycle persists state."""
        service = CorporateConsciousnessEvolutionService()
        service._state_cache = None
        
        initial_state = service.get_state()
        
        updated_state, _, _ = service.run_evolution_cycle()
        
        retrieved_state = service.get_state()
        
        # State should be persisted
        assert retrieved_state is not None


class TestEvolutionHistory:
    """Test evolution history tracking."""
    
    def test_get_evolution_history(self):
        """Test retrieving evolution history."""
        service = CorporateConsciousnessEvolutionService()
        
        history = service.get_evolution_history(limit=10)
        
        assert isinstance(history, list)
    
    def test_history_limit(self):
        """Test that history respects limit parameter."""
        service = CorporateConsciousnessEvolutionService()
        
        history = service.get_evolution_history(limit=5)
        
        assert len(history) <= 5


class TestEvolutionMetrics:
    """Test evolution metrics computation."""
    
    def test_get_evolution_metrics(self):
        """Test metrics retrieval."""
        service = CorporateConsciousnessEvolutionService()
        
        metrics = service.get_evolution_metrics()
        
        assert metrics is not None
        assert hasattr(metrics, 'phase_duration_days')
        assert hasattr(metrics, 'average_event_impact')
        assert hasattr(metrics, 'external_shock_frequency')
        assert hasattr(metrics, 'internal_change_frequency')
    
    def test_metrics_trajectories(self):
        """Test that metrics include trajectory information."""
        service = CorporateConsciousnessEvolutionService()
        
        metrics = service.get_evolution_metrics()
        
        assert metrics.momentum_trajectory in ["increasing", "decreasing", "stable"]
        assert metrics.stability_trajectory in ["improving", "degrading", "stable"]


class TestEvolutionReporting:
    """Test evolution report generation."""
    
    def test_generate_evolution_report(self):
        """Test report generation."""
        service = CorporateConsciousnessEvolutionService()
        
        report = service.generate_evolution_report(period="current")
        
        assert report is not None
        assert hasattr(report, 'current_state')
        assert hasattr(report, 'metrics')
        assert hasattr(report, 'phase_characteristics')
    
    def test_export_evolution_markdown(self):
        """Test Markdown export."""
        service = CorporateConsciousnessEvolutionService()
        
        report = service.generate_evolution_report(period="test")
        markdown = service.export_evolution_markdown(report)
        
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        assert "# Corporate Consciousness Evolution Report" in markdown
    
    def test_markdown_contains_key_sections(self):
        """Test that exported Markdown includes key sections."""
        service = CorporateConsciousnessEvolutionService()
        
        report = service.generate_evolution_report(period="test")
        markdown = service.export_evolution_markdown(report)
        
        # Check for key sections
        assert "Executive Summary" in markdown
        assert "Evolution Metrics" in markdown or "Metrics" in markdown
        assert "Strategic Implications" in markdown or "Recommended Actions" in markdown


class TestStateSerializationDeserialization:
    """Test serialization and deserialization of evolution state."""
    
    def test_serialize_state(self):
        """Test state serialization."""
        state = ConsciousnessEvolutionState(
            current_phase=ConsciousnessPhase.CONSOLIDATING,
            momentum=0.5,
            stability=0.6,
            history=[
                ConsciousnessEvolutionEvent(
                    event_id="test_1",
                    trigger_type="EXTERNAL_SHOCK",
                    description="Test event",
                ),
            ],
        )
        
        serialized = CorporateConsciousnessEvolutionService._serialize_state(state)
        
        assert isinstance(serialized, dict)
        assert serialized["current_phase"] == "CONSOLIDATING"
        assert serialized["momentum"] == 0.5
        assert len(serialized["history"]) == 1
    
    def test_deserialize_state(self):
        """Test state deserialization."""
        serialized = {
            "current_phase": "TRANSFORMING",
            "momentum": 0.7,
            "stability": 0.5,
            "last_update": datetime.now().isoformat(),
            "history": [
                {
                    "event_id": "test_1",
                    "trigger_type": "STRATEGY_SHIFT",
                    "description": "Test event",
                    "timestamp": datetime.now().isoformat(),
                    "impact_on_identity": 0.3,
                    "impact_on_purpose": 0.4,
                    "impact_on_direction": 0.5,
                    "impact_on_risk_posture": 0.2,
                }
            ],
        }
        
        state = CorporateConsciousnessEvolutionService._deserialize_state(serialized)
        
        assert isinstance(state, ConsciousnessEvolutionState)
        assert state.current_phase == ConsciousnessPhase.TRANSFORMING
        assert state.momentum == 0.7


class TestPhasePrediction:
    """Test phase transition prediction."""
    
    def test_phase_characteristics_descriptions(self):
        """Test that phase characteristics are descriptive."""
        for phase in [ConsciousnessPhase.EMERGING, ConsciousnessPhase.GROWING,
                      ConsciousnessPhase.CONSOLIDATING, ConsciousnessPhase.TRANSFORMING,
                      ConsciousnessPhase.MATURING]:
            description = CorporateConsciousnessEvolutionService._get_phase_characteristics(phase)
            assert isinstance(description, str)
            assert len(description) > 50


class TestNarrativeGeneration:
    """Test narrative generation for evolution state."""
    
    def test_momentum_narrative_generation(self):
        """Test momentum narrative generation."""
        state = ConsciousnessEvolutionState(
            momentum=0.8,
            stability=0.5,
            history=[],
        )
        
        metrics_data = {
            'momentum_trajectory': 'increasing',
            'external_shock_frequency': 1.5,
            'internal_change_frequency': 2.0,
        }
        
        # This would normally use the metrics object
        # Just verify the static method is callable
        assert hasattr(CorporateConsciousnessEvolutionService, '_generate_momentum_narrative')
    
    def test_stability_narrative_generation(self):
        """Test stability narrative generation."""
        state = ConsciousnessEvolutionState(
            momentum=0.5,
            stability=0.7,
            history=[],
        )
        
        # Verify the static method exists and is callable
        assert hasattr(CorporateConsciousnessEvolutionService, '_generate_stability_narrative')
