"""
Tests for Corporate Memory Service
===================================
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.backend.app.models.corporate_memory_model import (
    MemoryItemType,
    MemoryImportance,
    MemoryQuery,
)
from src.backend.app.services.corporate_memory_service import CorporateMemoryService


@pytest.fixture
def temp_data_dir(monkeypatch):
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


class TestServiceInit:
    """Tests for service initialization."""
    
    def test_service_initializes(self, temp_data_dir):
        """Test that service initializes without errors."""
        service = CorporateMemoryService()
        assert service is not None
        assert service.memory_store is not None

    def test_data_directory_created(self, temp_data_dir):
        """Test that data directory is created."""
        service = CorporateMemoryService()
        assert CorporateMemoryService.MEMORY_DIR.exists()


class TestMemoryPersistence:
    """Tests for memory persistence."""
    
    def test_add_memory_persists(self, temp_data_dir):
        """Test that added memories are persisted."""
        service = CorporateMemoryService()
        
        memory1 = service.add_memory(
            item_type=MemoryItemType.DECISION,
            title="Test Decision",
            description="A test decision",
            context={"test": True},
            importance=MemoryImportance.HIGH,
        )
        
        # Verify the file was created
        assert CorporateMemoryService.MEMORY_FILE.exists()
        
        # Load the file and verify data
        with open(CorporateMemoryService.MEMORY_FILE, 'r') as f:
            data = json.load(f)
            assert data['total_memories'] == 1
            assert len(data['memories']) == 1
            assert data['memories'][0]['title'] == "Test Decision"

    def test_load_persisted_memory(self, temp_data_dir):
        """Test loading persisted memories on service initialization."""
        # Create first service and add memory
        service1 = CorporateMemoryService()
        memory = service1.add_memory(
            item_type=MemoryItemType.DECISION,
            title="Persisted Decision",
            description="Should be loaded",
            context={},
        )
        memory_id = memory.memory_id
        
        # Create second service instance
        service2 = CorporateMemoryService()
        
        # Verify memory is loaded
        loaded_memory = service2.get_memory_by_id(memory_id)
        assert loaded_memory is not None
        assert loaded_memory.title == "Persisted Decision"
        assert service2.memory_store.total_memories == 1


class TestAddMemory:
    """Tests for adding memories via service."""
    
    def test_add_single_memory(self, temp_data_dir):
        """Test adding a single memory."""
        service = CorporateMemoryService()
        
        memory = service.add_memory(
            item_type=MemoryItemType.CRISIS_EVENT,
            title="System Outage",
            description="Database server went down",
            context={"duration_minutes": 45, "affected_users": 50000},
            importance=MemoryImportance.CRITICAL,
            tags=["incident", "database"],
        )
        
        assert memory.title == "System Outage"
        assert memory.importance == MemoryImportance.CRITICAL
        assert "incident" in memory.tags

    def test_add_multiple_memories(self, temp_data_dir):
        """Test adding multiple memories."""
        service = CorporateMemoryService()
        
        for i in range(5):
            service.add_memory(
                item_type=MemoryItemType.DECISION,
                title=f"Decision {i}",
                description=f"Description {i}",
                context={"index": i},
            )
        
        assert service.memory_store.total_memories == 5


class TestMemoryRetrieval:
    """Tests for retrieving memories."""
    
    def setup_method(self):
        """Setup test memories."""
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp()
        memory_dir = Path(self.temp_dir) / "corporate_memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Patch paths
        self.original_memory_dir = CorporateMemoryService.MEMORY_DIR
        self.original_memory_file = CorporateMemoryService.MEMORY_FILE
        CorporateMemoryService.MEMORY_DIR = memory_dir
        CorporateMemoryService.MEMORY_FILE = memory_dir / "memory.json"
        
        # Create service and add test memories
        self.service = CorporateMemoryService()
        
        for i in range(10):
            self.service.add_memory(
                item_type=MemoryItemType.DECISION if i % 2 == 0 else MemoryItemType.INTENT_CHANGE,
                title=f"Memory {i}",
                description=f"Description {i}",
                context={"index": i},
                importance=MemoryImportance.HIGH if i < 5 else MemoryImportance.MEDIUM,
            )

    def teardown_method(self):
        """Cleanup temp directory."""
        shutil.rmtree(self.temp_dir)
        CorporateMemoryService.MEMORY_DIR = self.original_memory_dir
        CorporateMemoryService.MEMORY_FILE = self.original_memory_file

    def test_get_all_memories(self):
        """Test getting all memories."""
        memories = self.service.get_all_memories()
        assert len(memories) == 10

    def test_get_memory_by_id(self):
        """Test getting a specific memory."""
        all_memories = self.service.get_all_memories()
        memory_id = all_memories[0].memory_id
        
        memory = self.service.get_memory_by_id(memory_id)
        assert memory is not None
        assert memory.memory_id == memory_id

    def test_get_memories_by_type(self):
        """Test getting memories by type."""
        decisions = self.service.get_memories_by_type(MemoryItemType.DECISION)
        intent_changes = self.service.get_memories_by_type(MemoryItemType.INTENT_CHANGE)
        
        assert len(decisions) == 5
        assert len(intent_changes) == 5

    def test_query_memories(self):
        """Test querying memories with filters."""
        query = MemoryQuery(
            item_types=[MemoryItemType.DECISION],
            importance_levels=[MemoryImportance.HIGH],
        )
        
        result = self.service.query_memories(query)
        assert result.total_count == 3  # 5 decisions, but only first 3 are HIGH importance


class TestMemorySummary:
    """Tests for memory summary."""
    
    def setup_method(self):
        """Setup test memories."""
        self.temp_dir = tempfile.mkdtemp()
        memory_dir = Path(self.temp_dir) / "corporate_memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.original_memory_dir = CorporateMemoryService.MEMORY_DIR
        self.original_memory_file = CorporateMemoryService.MEMORY_FILE
        CorporateMemoryService.MEMORY_DIR = memory_dir
        CorporateMemoryService.MEMORY_FILE = memory_dir / "memory.json"
        
        self.service = CorporateMemoryService()
        
        # Add test memories
        self.service.add_memory(
            item_type=MemoryItemType.CRISIS_EVENT,
            title="Critical Incident",
            description="Major issue",
            context={},
            importance=MemoryImportance.CRITICAL,
        )
        
        for i in range(5):
            self.service.add_memory(
                item_type=MemoryItemType.DECISION,
                title=f"Decision {i}",
                description=f"Description {i}",
                context={},
                importance=MemoryImportance.HIGH,
            )

    def teardown_method(self):
        """Cleanup temp directory."""
        shutil.rmtree(self.temp_dir)
        CorporateMemoryService.MEMORY_DIR = self.original_memory_dir
        CorporateMemoryService.MEMORY_FILE = self.original_memory_file

    def test_get_memory_summary(self):
        """Test getting memory summary."""
        summary = self.service.get_memory_summary()
        
        assert summary.total_memories == 6
        assert len(summary.recent_memories) > 0
        assert len(summary.critical_memories) > 0

    def test_summary_includes_metrics(self):
        """Test that summary includes important metrics."""
        summary = self.service.get_memory_summary()
        
        assert summary.total_memories >= 0
        assert isinstance(summary.memory_types, dict)
        assert isinstance(summary.importance_distribution, dict)


class TestMemoryExport:
    """Tests for memory export."""
    
    def setup_method(self):
        """Setup test memories."""
        self.temp_dir = tempfile.mkdtemp()
        memory_dir = Path(self.temp_dir) / "corporate_memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.original_memory_dir = CorporateMemoryService.MEMORY_DIR
        self.original_memory_file = CorporateMemoryService.MEMORY_FILE
        CorporateMemoryService.MEMORY_DIR = memory_dir
        CorporateMemoryService.MEMORY_FILE = memory_dir / "memory.json"
        
        self.service = CorporateMemoryService()
        self.memory = self.service.add_memory(
            item_type=MemoryItemType.DECISION,
            title="Export Test",
            description="Memory for export test",
            context={"key": "value"},
        )

    def teardown_method(self):
        """Cleanup temp directory."""
        shutil.rmtree(self.temp_dir)
        CorporateMemoryService.MEMORY_DIR = self.original_memory_dir
        CorporateMemoryService.MEMORY_FILE = self.original_memory_file

    def test_export_single_memory_markdown(self):
        """Test exporting single memory as markdown."""
        markdown = self.service.export_memory_markdown(self.memory.memory_id)
        
        assert markdown is not None
        assert "Export Test" in markdown
        assert "Memory for export test" in markdown

    def test_export_all_memories_markdown(self):
        """Test exporting all memories as markdown."""
        markdown = self.service.export_memory_markdown()
        
        assert markdown is not None
        assert "Corporate Memory Export" in markdown
        assert "Export Test" in markdown


class TestHelperMethods:
    """Tests for helper methods."""
    
    def setup_method(self):
        """Setup service."""
        self.temp_dir = tempfile.mkdtemp()
        memory_dir = Path(self.temp_dir) / "corporate_memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.original_memory_dir = CorporateMemoryService.MEMORY_DIR
        self.original_memory_file = CorporateMemoryService.MEMORY_FILE
        CorporateMemoryService.MEMORY_DIR = memory_dir
        CorporateMemoryService.MEMORY_FILE = memory_dir / "memory.json"
        
        self.service = CorporateMemoryService()

    def teardown_method(self):
        """Cleanup temp directory."""
        shutil.rmtree(self.temp_dir)
        CorporateMemoryService.MEMORY_DIR = self.original_memory_dir
        CorporateMemoryService.MEMORY_FILE = self.original_memory_file

    def test_record_intent_change(self):
        """Test recording intent change."""
        old = {"mission": "Old"}
        new = {"mission": "New"}
        
        memory = self.service.record_intent_change(old, new, "Market shift")
        
        assert memory.item_type == MemoryItemType.INTENT_CHANGE
        assert memory.importance == MemoryImportance.HIGH

    def test_record_decision(self):
        """Test recording decision."""
        memory = self.service.record_decision(
            decision_id="dec_001",
            decision_desc="Acquire company",
            reasoning="Strategic fit",
            supporting_roles=["CEO"],
            opposing_roles=["CFO"],
        )
        
        assert memory.item_type == MemoryItemType.DECISION
        assert "CEO" in str(memory.context)

    def test_record_consciousness_evolution(self):
        """Test recording consciousness evolution."""
        memory = self.service.record_consciousness_evolution(
            old_phase="Learning",
            new_phase="Mastering",
            milestone="Achieved 95% accuracy",
        )
        
        assert memory.item_type == MemoryItemType.CONSCIOUSNESS_EVOLUTION
        assert "Learning" in memory.description
