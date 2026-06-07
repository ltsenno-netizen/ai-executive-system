"""
Tests for Corporate Consciousness Service (Step AE)

Tests the service layer for consciousness lifecycle management:
- Consciousness generation with all data sources
- Caching and persistence
- Retrieval operations
- Markdown export
"""

import pytest
import os
import json
from pathlib import Path
from datetime import datetime
from src.backend.app.services.corporate_consciousness_service import CorporateConsciousnessService
from src.backend.app.models.corporate_consciousness_model import CorporateConsciousness


@pytest.fixture
def consciousness_service():
    """Create a consciousness service instance"""
    return CorporateConsciousnessService()


@pytest.fixture
def test_period():
    """Standard test period"""
    return "2026-01"


class TestConsciousnessServiceInitialization:
    """Test service initialization"""

    def test_service_initializes(self, consciousness_service):
        """Test service can be instantiated"""
        assert consciousness_service is not None

    def test_service_has_required_methods(self, consciousness_service):
        """Test service has all required methods"""
        required_methods = [
            "generate_consciousness",
            "get_consciousness",
            "get_latest_consciousness",
            "get_consciousness_summary",
            "update_consciousness",
            "compute_consciousness_metrics",
            "export_consciousness_markdown",
            "get_consciousness_history",
        ]
        for method_name in required_methods:
            assert hasattr(consciousness_service, method_name), f"Missing method: {method_name}"

    def test_data_directory_created(self, consciousness_service):
        """Test data directory is created"""
        assert os.path.exists(consciousness_service.data_dir)


class TestConsciousnessGeneration:
    """Test consciousness generation"""

    def test_consciousness_can_be_generated(self, consciousness_service, test_period):
        """Test consciousness can be generated for a period"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        assert consciousness is not None
        assert isinstance(consciousness, CorporateConsciousness)
        assert consciousness.overall_consciousness_score > 0
        assert consciousness.identity_statement is not None

    def test_consciousness_persists_to_file(self, consciousness_service, test_period):
        """Test consciousness is saved to file"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        file_path = consciousness_service.data_dir / f"consciousness_{test_period}.json"
        assert file_path.exists(), f"Consciousness file not found at {file_path}"

    def test_consciousness_includes_quality_metrics(self, consciousness_service, test_period):
        """Test consciousness includes quality metrics"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        assert consciousness.overall_consciousness_score > 0
        assert consciousness.clarity_score > 0
        assert consciousness.coherence_score > 0
        assert consciousness.alignment_score > 0
        assert consciousness.authenticity_score > 0


class TestConsciousnessRetrieval:
    """Test consciousness retrieval operations"""

    def test_consciousness_can_be_retrieved(self, consciousness_service, test_period):
        """Test consciousness can be retrieved by period"""
        # Generate first
        generated = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        # Retrieve
        retrieved = consciousness_service.get_consciousness(test_period)
        assert retrieved is not None
        assert retrieved.period == test_period
        assert retrieved.overall_consciousness_score == generated.overall_consciousness_score

    def test_latest_consciousness_retrieved(self, consciousness_service, test_period):
        """Test latest consciousness can be retrieved"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        latest = consciousness_service.get_latest_consciousness()
        assert latest is not None
        assert latest.period == consciousness.period

    def test_consciousness_summary_retrieved(self, consciousness_service, test_period):
        """Test consciousness summary can be retrieved for dashboard"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        summary = consciousness_service.get_consciousness_summary(test_period)
        assert summary is not None
        assert summary.identity_statement is not None
        assert summary.purpose_statement is not None
        assert summary.strategic_direction is not None
        assert summary.overall_score > 0


class TestConsciousnessUpdate:
    """Test consciousness update operations"""

    def test_consciousness_can_be_updated(self, consciousness_service, test_period):
        """Test consciousness can be regenerated"""
        consciousness1 = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        # Update
        consciousness2 = consciousness_service.update_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        assert consciousness2 is not None
        # Update should be a fresh generation
        assert consciousness2.period == consciousness1.period


class TestConsciousnessMetrics:
    """Test consciousness quality metrics"""

    def test_metrics_computed(self, consciousness_service, test_period):
        """Test quality metrics are computed"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        metrics = consciousness_service.compute_consciousness_metrics(consciousness)
        
        assert metrics is not None
        assert "overall_score" in metrics
        assert "clarity_score" in metrics
        assert "coherence_score" in metrics
        assert "alignment_score" in metrics
        assert "authenticity_score" in metrics
        assert "model_coherence" in metrics
        assert "self_awareness_level" in metrics

    def test_all_metrics_in_valid_range(self, consciousness_service, test_period):
        """Test all metrics are in 0-1 range"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        metrics = consciousness_service.compute_consciousness_metrics(consciousness)
        
        for key, value in metrics.items():
            assert 0 <= value <= 1, f"Metric {key}={value} out of range [0,1]"


class TestConsciousnessMarkdownExport:
    """Test markdown export"""

    def test_markdown_export_generated(self, consciousness_service, test_period):
        """Test markdown export can be generated"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        markdown = consciousness_service.export_consciousness_markdown(consciousness)
        
        assert markdown is not None
        assert len(markdown) > 0
        assert "# Corporate Consciousness Report" in markdown or "Consciousness" in markdown

    def test_markdown_includes_key_sections(self, consciousness_service, test_period):
        """Test markdown includes key sections"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        markdown = consciousness_service.export_consciousness_markdown(consciousness)
        
        # Should include identity, purpose, direction
        assert "identity" in markdown.lower() or "Identity" in markdown
        assert "purpose" in markdown.lower() or "Purpose" in markdown
        assert "direction" in markdown.lower() or "Direction" in markdown


class TestConsciousnessHistory:
    """Test consciousness history operations"""

    def test_consciousness_history_retrieved(self, consciousness_service):
        """Test consciousness history can be retrieved"""
        # Generate multiple consciousness records
        for i in range(1, 4):
            consciousness_service.generate_consciousness(
                period=f"2026-{i:02d}",
                company_name="TestCorp",
            )
        
        history = consciousness_service.get_consciousness_history(limit=5)
        
        assert history is not None
        assert len(history) > 0

    def test_history_limit_respected(self, consciousness_service):
        """Test history limit is respected"""
        # Generate multiple records
        for i in range(1, 8):
            consciousness_service.generate_consciousness(
                period=f"2026-{i:02d}",
                company_name="TestCorp",
            )
        
        history = consciousness_service.get_consciousness_history(limit=3)
        
        assert len(history) <= 3


class TestConsciousnessIntegrationWithOtherServices:
    """Test consciousness service integration"""

    def test_consciousness_integrates_intent(self, consciousness_service, test_period):
        """Test consciousness integrates corporate intent"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        # Should have integrated intent through synthesis
        assert consciousness.self_model.meta_decision_synthesis is not None

    def test_consciousness_integrates_agents(self, consciousness_service, test_period):
        """Test consciousness integrates executive agents"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        # Should have integrated agents through synthesis
        assert consciousness.self_model.meta_decision_synthesis.agent_contribution is not None

    def test_consciousness_integrates_frontier(self, consciousness_service, test_period):
        """Test consciousness integrates frontier optimization"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        # Should have integrated frontier through synthesis
        assert consciousness.self_model.meta_decision_synthesis.frontier_contribution is not None


class TestConsciousnessDataConsistency:
    """Test data consistency"""

    def test_consciousness_period_consistent(self, consciousness_service, test_period):
        """Test period is consistently recorded"""
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name="TestCorp",
        )
        
        assert consciousness.period == test_period
        summary = consciousness_service.get_consciousness_summary(test_period)
        assert summary.period == test_period

    def test_consciousness_company_name_preserved(self, consciousness_service, test_period):
        """Test company name is preserved"""
        company_name = "MyCorp Inc"
        consciousness = consciousness_service.generate_consciousness(
            period=test_period,
            company_name=company_name,
        )
        
        assert consciousness.company_name == company_name
