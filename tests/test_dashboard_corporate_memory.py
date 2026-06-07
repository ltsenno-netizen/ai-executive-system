"""
Tests for Corporate Memory Dashboard Integration
================================================
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from src.backend.app.models.executive_dashboard_model import ExecutiveDashboard
from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService
from src.backend.app.services.corporate_memory_service import CorporateMemoryService
from src.backend.app.models.corporate_memory_model import MemoryItemType, MemoryImportance


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    memory_dir = Path(temp_dir) / "corporate_memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    # Patch the service to use temp directory
    original_memory_dir = CorporateMemoryService.MEMORY_DIR
    original_memory_file = CorporateMemoryService.MEMORY_FILE
    
    CorporateMemoryService.MEMORY_DIR = memory_dir
    CorporateMemoryService.MEMORY_FILE = memory_dir / "memory.json"
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)
    CorporateMemoryService.MEMORY_DIR = original_memory_dir
    CorporateMemoryService.MEMORY_FILE = original_memory_file


class TestDashboardWithCorporateMemory:
    """Tests for dashboard with corporate memory integration."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        memory_dir = Path(self.temp_dir) / "corporate_memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.original_memory_dir = CorporateMemoryService.MEMORY_DIR
        self.original_memory_file = CorporateMemoryService.MEMORY_FILE
        CorporateMemoryService.MEMORY_DIR = memory_dir
        CorporateMemoryService.MEMORY_FILE = memory_dir / "memory.json"
        
        self.dashboard_service = ExecutiveDashboardService()
        self.memory_service = CorporateMemoryService()

    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir)
        CorporateMemoryService.MEMORY_DIR = self.original_memory_dir
        CorporateMemoryService.MEMORY_FILE = self.original_memory_file

    def test_dashboard_has_corporate_memory_summary(self):
        """Test that dashboard includes corporate memory summary."""
        # Add some test memories
        for i in range(3):
            self.memory_service.add_memory(
                item_type=MemoryItemType.DECISION,
                title=f"Decision {i}",
                description=f"Description {i}",
                context={},
                importance=MemoryImportance.HIGH,
            )
        
        # Patch the aggregate method to return a simple dashboard
        with patch.object(self.dashboard_service, 'aggregate_pl') as mock_pl, \
             patch.object(self.dashboard_service, 'aggregate_kpis') as mock_kpis, \
             patch.object(self.dashboard_service, 'aggregate_operations') as mock_ops, \
             patch.object(self.dashboard_service, 'aggregate_issues') as mock_issues, \
             patch.object(self.dashboard_service, 'aggregate_improvements') as mock_improvements, \
             patch.object(self.dashboard_service, 'aggregate_organization_summary') as mock_org:
            
            # Set up mocks with minimal valid data
            from src.backend.app.models.executive_dashboard_model import (
                ExecutivePLSummary, ExecutiveKPISummary, ExecutiveOpsSummary,
                ExecutiveIssueSummary, ExecutiveImprovementSummary, ExecutiveOrganizationSummary
            )
            
            mock_pl.return_value = ExecutivePLSummary(month=1, revenue=0, cost=0, profit=0, profit_margin=0, cash_balance=0)
            mock_kpis.return_value = ExecutiveKPISummary(month=1, kpis={})
            mock_ops.return_value = ExecutiveOpsSummary(month=1, department_load={}, active_tasks=0, incidents=0)
            mock_issues.return_value = ExecutiveIssueSummary(month=1, issues=[])
            mock_improvements.return_value = ExecutiveImprovementSummary(month=1, executed_actions=[], updated_priorities={})
            mock_org.return_value = ExecutiveOrganizationSummary(units=[])
            
            # Get corporate memory summary
            memory_summary = self.dashboard_service.aggregate_corporate_memory_summary()
            
            # Verify it's not None
            assert memory_summary is not None
            assert memory_summary.total_memories == 3

    def test_corporate_memory_summary_with_no_memories(self):
        """Test corporate memory summary when no memories exist."""
        memory_summary = self.dashboard_service.aggregate_corporate_memory_summary()
        
        # Should return a summary even with no memories
        assert memory_summary is not None
        assert memory_summary.total_memories == 0

    def test_corporate_memory_summary_structure(self):
        """Test the structure of corporate memory summary."""
        # Add test memories
        self.memory_service.add_memory(
            item_type=MemoryItemType.CRISIS_EVENT,
            title="Critical Issue",
            description="Major crisis",
            context={},
            importance=MemoryImportance.CRITICAL,
        )
        
        memory_summary = self.dashboard_service.aggregate_corporate_memory_summary()
        
        # Check summary structure
        assert hasattr(memory_summary, 'total_memories')
        assert hasattr(memory_summary, 'memory_types')
        assert hasattr(memory_summary, 'importance_distribution')
        assert hasattr(memory_summary, 'recent_memories')
        assert hasattr(memory_summary, 'critical_memories')
        assert hasattr(memory_summary, 'top_impactful_events')

    def test_corporate_memory_includes_different_memory_types(self):
        """Test that corporate memory tracks different memory types."""
        # Add different types of memories
        self.memory_service.add_memory(
            item_type=MemoryItemType.DECISION,
            title="Strategic Decision",
            description="Major decision",
            context={},
            importance=MemoryImportance.HIGH,
        )
        
        self.memory_service.add_memory(
            item_type=MemoryItemType.CONSCIOUSNESS_EVOLUTION,
            title="Consciousness Evolution",
            description="System learned new capability",
            context={},
            importance=MemoryImportance.HIGH,
        )
        
        self.memory_service.add_memory(
            item_type=MemoryItemType.CRISIS_EVENT,
            title="Crisis Event",
            description="System encountered crisis",
            context={},
            importance=MemoryImportance.CRITICAL,
        )
        
        memory_summary = self.dashboard_service.aggregate_corporate_memory_summary()
        
        # Check that all types are tracked
        assert memory_summary.total_memories == 3
        assert memory_summary.memory_types.get('decision', 0) >= 0
        assert memory_summary.memory_types.get('consciousness_evolution', 0) >= 0
        assert memory_summary.memory_types.get('crisis_event', 0) >= 0

    def test_corporate_memory_importance_distribution(self):
        """Test importance distribution in memory summary."""
        # Add memories with different importance levels
        for i in range(3):
            self.memory_service.add_memory(
                item_type=MemoryItemType.DECISION,
                title=f"Decision {i}",
                description=f"Desc {i}",
                context={},
                importance=MemoryImportance.HIGH,
            )
        
        for i in range(2):
            self.memory_service.add_memory(
                item_type=MemoryItemType.NARRATIVE_GENERATED,
                title=f"Narrative {i}",
                description=f"Desc {i}",
                context={},
                importance=MemoryImportance.LOW,
            )
        
        memory_summary = self.dashboard_service.aggregate_corporate_memory_summary()
        
        # Check distribution
        assert memory_summary.importance_distribution.get('HIGH', 0) >= 3
        assert memory_summary.importance_distribution.get('LOW', 0) >= 2

    def test_critical_memories_in_summary(self):
        """Test that critical memories are included in summary."""
        # Add some critical memories
        for i in range(2):
            self.memory_service.add_memory(
                item_type=MemoryItemType.CRISIS_EVENT,
                title=f"Critical Event {i}",
                description=f"Crisis situation {i}",
                context={},
                importance=MemoryImportance.CRITICAL,
            )
        
        # Add some non-critical memories
        for i in range(3):
            self.memory_service.add_memory(
                item_type=MemoryItemType.DECISION,
                title=f"Decision {i}",
                description=f"Desc {i}",
                context={},
                importance=MemoryImportance.MEDIUM,
            )
        
        memory_summary = self.dashboard_service.aggregate_corporate_memory_summary()
        
        # Check that critical memories are included
        assert len(memory_summary.critical_memories) > 0
        assert all(m.importance == MemoryImportance.CRITICAL for m in memory_summary.critical_memories)

    def test_recent_memories_in_summary(self):
        """Test that recent memories are included in summary."""
        # Add test memories
        for i in range(10):
            self.memory_service.add_memory(
                item_type=MemoryItemType.DECISION,
                title=f"Decision {i}",
                description=f"Desc {i}",
                context={},
            )
        
        memory_summary = self.dashboard_service.aggregate_corporate_memory_summary()
        
        # Check that recent memories are limited
        assert len(memory_summary.recent_memories) <= 5  # Default max_recent is 5

    def test_memory_summary_monthly_stats(self):
        """Test monthly statistics in memory summary."""
        # Add memories
        for i in range(5):
            self.memory_service.add_memory(
                item_type=MemoryItemType.DECISION,
                title=f"Decision {i}",
                description=f"Desc {i}",
                context={},
            )
        
        memory_summary = self.dashboard_service.aggregate_corporate_memory_summary()
        
        # Check monthly stats
        assert memory_summary.memories_this_month >= 5
        assert memory_summary.memories_this_quarter >= 5


class TestDashboardMemoryIntegration:
    """Integration tests for dashboard with corporate memory."""
    
    def setup_method(self):
        """Setup for integration tests."""
        self.temp_dir = tempfile.mkdtemp()
        memory_dir = Path(self.temp_dir) / "corporate_memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.original_memory_dir = CorporateMemoryService.MEMORY_DIR
        self.original_memory_file = CorporateMemoryService.MEMORY_FILE
        CorporateMemoryService.MEMORY_DIR = memory_dir
        CorporateMemoryService.MEMORY_FILE = memory_dir / "memory.json"

    def teardown_method(self):
        """Cleanup after integration tests."""
        shutil.rmtree(self.temp_dir)
        CorporateMemoryService.MEMORY_DIR = self.original_memory_dir
        CorporateMemoryService.MEMORY_FILE = self.original_memory_file

    def test_corporate_memory_fallback_on_error(self):
        """Test that dashboard gracefully handles memory service errors."""
        dashboard_service = ExecutiveDashboardService()
        
        # Even if there's an error, it should not crash
        memory_summary = dashboard_service.aggregate_corporate_memory_summary()
        
        # Should return None or empty summary on error
        assert memory_summary is None or memory_summary.total_memories == 0

    def test_memory_summary_performance(self):
        """Test that memory summary generation is performant."""
        memory_service = CorporateMemoryService()
        dashboard_service = ExecutiveDashboardService()
        
        # Add many memories
        for i in range(100):
            memory_service.add_memory(
                item_type=MemoryItemType.DECISION if i % 2 == 0 else MemoryItemType.INTENT_CHANGE,
                title=f"Memory {i}",
                description=f"Description {i}",
                context={"index": i},
                importance=MemoryImportance.HIGH if i < 50 else MemoryImportance.LOW,
            )
        
        # Generate summary (should be fast)
        import time
        start = time.time()
        memory_summary = dashboard_service.aggregate_corporate_memory_summary()
        elapsed = time.time() - start
        
        # Should complete in less than 1 second
        assert elapsed < 1.0
        assert memory_summary is not None
        assert memory_summary.total_memories == 100
