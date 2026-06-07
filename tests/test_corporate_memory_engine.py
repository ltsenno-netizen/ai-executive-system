"""
Tests for Corporate Memory Engine
==================================
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from src.backend.app.models.corporate_memory_model import (
    MemoryItem,
    MemoryItemType,
    MemoryImportance,
    CorporateMemory,
    MemoryQuery,
)
from src.backend.app.services.corporate_memory_engine import CorporateMemoryEngine


@pytest.fixture
def memory_store():
    """Create a fresh memory store for each test."""
    return CorporateMemory()


@pytest.fixture
def sample_context():
    """Create sample context data."""
    return {
        "decision_id": "dec_001",
        "supporting_roles": ["CEO", "CFO"],
        "opposing_roles": ["CTO"],
        "reasoning": "Market demand increase detected",
    }


class TestAddMemory:
    """Tests for adding memories."""
    
    def test_add_basic_memory(self, memory_store):
        """Test adding a basic memory."""
        memory = CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.DECISION,
            title="Budget Increase",
            description="Approved budget increase for R&D",
            context={"amount": 1000000},
            importance=MemoryImportance.HIGH,
        )
        
        assert memory is not None
        assert memory.title == "Budget Increase"
        assert memory.item_type == MemoryItemType.DECISION
        assert memory.importance == MemoryImportance.HIGH
        assert memory_store.total_memories == 1

    def test_add_memory_auto_importance(self, memory_store):
        """Test that importance is auto-determined for known types."""
        memory = CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.CRISIS_EVENT,
            title="Security Breach",
            description="Data breach detected",
            context={"affected_customers": 10000},
        )
        
        # Crisis events should default to CRITICAL
        assert memory.importance == MemoryImportance.CRITICAL

    def test_add_memory_with_tags(self, memory_store):
        """Test adding memory with tags."""
        memory = CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.DECISION,
            title="Partnership Decision",
            description="Decided to partner with company X",
            context={},
            tags=["partnership", "strategic", "external"],
        )
        
        assert memory.tags == ["partnership", "strategic", "external"]

    def test_memory_store_statistics_updated(self, memory_store):
        """Test that memory store statistics are updated."""
        CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.DECISION,
            title="Memory 1",
            description="Description 1",
            context={},
            importance=MemoryImportance.HIGH,
        )
        
        CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.DECISION,
            title="Memory 2",
            description="Description 2",
            context={},
            importance=MemoryImportance.CRITICAL,
        )
        
        assert memory_store.total_memories == 2
        assert memory_store.type_distribution["DECISION"] == 2
        assert memory_store.importance_distribution["HIGH"] == 1
        assert memory_store.importance_distribution["CRITICAL"] == 1


class TestQueryMemories:
    """Tests for querying memories."""
    
    def setup_method(self):
        """Setup memories for tests."""
        self.store = CorporateMemory()
        now = datetime.utcnow()
        
        # Add test memories
        for i in range(10):
            CorporateMemoryEngine.add_memory(
                memory_store=self.store,
                item_type=MemoryItemType.DECISION if i % 2 == 0 else MemoryItemType.INTENT_CHANGE,
                title=f"Memory {i}",
                description=f"Description for memory {i}",
                context={"index": i},
                importance=MemoryImportance.HIGH if i < 5 else MemoryImportance.MEDIUM,
                tags=["test", "sample"] if i % 2 == 0 else ["test"],
            )

    def test_query_all_memories(self):
        """Test querying all memories."""
        query = MemoryQuery()
        result = CorporateMemoryEngine.query_memories(self.store, query)
        
        assert result.total_count == 10
        assert len(result.memories) == 10

    def test_query_by_type(self):
        """Test querying by memory type."""
        query = MemoryQuery(item_types=[MemoryItemType.DECISION])
        result = CorporateMemoryEngine.query_memories(self.store, query)
        
        assert result.total_count == 5
        assert all(m.item_type == MemoryItemType.DECISION for m in result.memories)

    def test_query_by_importance(self):
        """Test querying by importance."""
        query = MemoryQuery(importance_levels=[MemoryImportance.HIGH])
        result = CorporateMemoryEngine.query_memories(self.store, query)
        
        assert result.total_count == 5
        assert all(m.importance == MemoryImportance.HIGH for m in result.memories)

    def test_query_with_pagination(self):
        """Test pagination."""
        query = MemoryQuery(limit=3, offset=0)
        result1 = CorporateMemoryEngine.query_memories(self.store, query)
        
        assert len(result1.memories) == 3
        assert result1.total_count == 10
        
        query = MemoryQuery(limit=3, offset=3)
        result2 = CorporateMemoryEngine.query_memories(self.store, query)
        
        assert len(result2.memories) == 3
        assert result1.memories[0].memory_id != result2.memories[0].memory_id

    def test_query_by_tag(self):
        """Test querying by tags."""
        query = MemoryQuery(tags=["sample"])
        result = CorporateMemoryEngine.query_memories(self.store, query)
        
        assert result.total_count == 5
        assert all("sample" in m.tags for m in result.memories)

    def test_query_by_search_text(self):
        """Test full-text search."""
        query = MemoryQuery(search_text="Memory 5")
        result = CorporateMemoryEngine.query_memories(self.store, query)
        
        assert result.total_count >= 1
        assert any("Memory 5" in m.title for m in result.memories)

    def test_query_combined_filters(self):
        """Test combining multiple filters."""
        query = MemoryQuery(
            item_types=[MemoryItemType.DECISION],
            importance_levels=[MemoryImportance.HIGH],
            tags=["sample"],
        )
        result = CorporateMemoryEngine.query_memories(self.store, query)
        
        assert all(m.item_type == MemoryItemType.DECISION for m in result.memories)
        assert all(m.importance == MemoryImportance.HIGH for m in result.memories)
        assert all("sample" in m.tags for m in result.memories)


class TestTimeDecayAndWeighting:
    """Tests for time decay and importance weighting."""
    
    def test_compute_effective_weight_recent_high_importance(self, memory_store):
        """Test weight calculation for recent high-importance memory."""
        memory = CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.CRISIS_EVENT,
            title="Recent Crisis",
            description="Just happened",
            context={},
            importance=MemoryImportance.CRITICAL,
        )
        
        weight = CorporateMemoryEngine.compute_effective_weight(memory)
        
        # Should be close to 1.0 for recent critical memory
        assert 0.8 < weight <= 1.0

    def test_compute_effective_weight_old_low_importance(self, memory_store):
        """Test weight calculation for old low-importance memory."""
        memory = CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.NARRATIVE_GENERATED,
            title="Old Narrative",
            description="Generated long ago",
            context={},
            importance=MemoryImportance.LOW,
        )
        
        # Simulate memory being 180 days old
        memory.timestamp = datetime.utcnow() - timedelta(days=180)
        
        weight = CorporateMemoryEngine.compute_effective_weight(memory)
        
        # Should be significantly lower due to age and low importance
        assert weight < 0.2

    def test_compute_effective_weight_with_access_count(self, memory_store):
        """Test that access count boosts weight."""
        memory = CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.DECISION,
            title="Frequently Accessed",
            description="Memory that's accessed often",
            context={},
            importance=MemoryImportance.HIGH,
        )
        
        weight_no_access = CorporateMemoryEngine.compute_effective_weight(memory)
        
        # Simulate 10 accesses
        memory.access_count = 10
        weight_with_access = CorporateMemoryEngine.compute_effective_weight(memory)
        
        # Weight should increase with access
        assert weight_with_access > weight_no_access


class TestMemorySummary:
    """Tests for memory summary generation."""
    
    def setup_method(self):
        """Setup memories for tests."""
        self.store = CorporateMemory()
        
        # Add various types of memories
        CorporateMemoryEngine.add_memory(
            memory_store=self.store,
            item_type=MemoryItemType.CRISIS_EVENT,
            title="Security Incident",
            description="Data breach",
            context={},
            importance=MemoryImportance.CRITICAL,
        )
        
        for i in range(5):
            CorporateMemoryEngine.add_memory(
                memory_store=self.store,
                item_type=MemoryItemType.DECISION,
                title=f"Decision {i}",
                description=f"Description {i}",
                context={},
                importance=MemoryImportance.HIGH,
            )

    def test_get_memory_summary(self):
        """Test memory summary generation."""
        summary = CorporateMemoryEngine.get_memory_summary(self.store)
        
        assert summary.total_memories == 6
        assert summary.memories_this_month >= 6
        assert len(summary.recent_memories) > 0
        assert len(summary.top_impactful_events) > 0

    def test_get_memory_summary_max_recent(self):
        """Test max_recent parameter."""
        summary = CorporateMemoryEngine.get_memory_summary(self.store, max_recent=2)
        
        assert len(summary.recent_memories) <= 2

    def test_get_memory_summary_max_critical(self):
        """Test max_critical parameter."""
        summary = CorporateMemoryEngine.get_memory_summary(self.store, max_critical=1)
        
        assert len(summary.critical_memories) <= 1


class TestMemoryExport:
    """Tests for memory export functionality."""
    
    def test_export_single_memory_markdown(self, memory_store):
        """Test exporting a single memory as markdown."""
        memory = CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.DECISION,
            title="Strategic Partnership",
            description="Partnership with company X established",
            context={"partner": "CompanyX", "value": 5000000},
            importance=MemoryImportance.HIGH,
            tags=["partnership", "strategic"],
        )
        
        markdown = CorporateMemoryEngine.get_memory_markdown_export(memory_store, memory.memory_id)
        
        assert markdown is not None
        assert "Strategic Partnership" in markdown
        assert "partnership" in markdown
        assert "CompanyX" in markdown

    def test_export_all_memories_markdown(self, memory_store):
        """Test exporting all memories as markdown."""
        for i in range(3):
            CorporateMemoryEngine.add_memory(
                memory_store=memory_store,
                item_type=MemoryItemType.DECISION,
                title=f"Memory {i}",
                description=f"Description {i}",
                context={},
            )
        
        markdown = CorporateMemoryEngine.get_all_memories_markdown_export(memory_store)
        
        assert markdown is not None
        assert "Corporate Memory Export" in markdown
        assert "Memory 0" in markdown
        assert "Memory 1" in markdown
        assert "Memory 2" in markdown


class TestHelperMethods:
    """Tests for helper methods."""
    
    def test_record_intent_change(self, memory_store):
        """Test recording intent change."""
        old_intent = {"mission": "Old mission"}
        new_intent = {"mission": "New mission"}
        
        memory = CorporateMemoryEngine.record_intent_change(
            memory_store=memory_store,
            old_intent=old_intent,
            new_intent=new_intent,
            reason="Market shift detected",
        )
        
        assert memory.item_type == MemoryItemType.INTENT_CHANGE
        assert memory.importance == MemoryImportance.HIGH
        assert "Market shift" in memory.description

    def test_record_decision(self, memory_store):
        """Test recording a decision."""
        memory = CorporateMemoryEngine.record_decision(
            memory_store=memory_store,
            decision_id="dec_001",
            decision_desc="Acquire Company Y",
            reasoning="Strategic fit and synergies",
            supporting_roles=["CEO", "Board"],
            opposing_roles=["CFO"],
        )
        
        assert memory.item_type == MemoryItemType.DECISION
        assert memory.importance == MemoryImportance.HIGH
        assert "Board" in str(memory.context)

    def test_record_consciousness_evolution(self, memory_store):
        """Test recording consciousness evolution."""
        memory = CorporateMemoryEngine.record_consciousness_evolution(
            memory_store=memory_store,
            old_phase="Learning",
            new_phase="Mastering",
            milestone="Achieved 95% accuracy",
        )
        
        assert memory.item_type == MemoryItemType.CONSCIOUSNESS_EVOLUTION
        assert memory.importance == MemoryImportance.HIGH
        assert "Learning" in memory.description
        assert "Mastering" in memory.description
