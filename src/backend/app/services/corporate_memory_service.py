"""
Corporate Memory Service
========================

Service layer for corporate memory that manages persistence,
retrieval, and high-level operations.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from .corporate_memory_engine import CorporateMemoryEngine
from ..models.corporate_memory_model import (
    MemoryItem,
    MemoryItemType,
    MemoryImportance,
    CorporateMemory,
    MemoryQuery,
    MemoryQueryResult,
    CorporateMemorySummary,
)


class CorporateMemoryService:
    """Service for managing corporate memory operations."""
    
    MEMORY_DIR = Path("data/corporate_memory")
    MEMORY_FILE = Path("data/corporate_memory/memory.json")
    
    def __init__(self):
        """Initialize the corporate memory service."""
        self.engine = CorporateMemoryEngine()
        self.memory_store: Optional[CorporateMemory] = None
        self._ensure_data_directory()
        self._load_memory()
    
    def _ensure_data_directory(self):
        """Ensure the memory data directory exists."""
        self.MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_memory(self):
        """Load memory from persistent storage."""
        if self.MEMORY_FILE.exists():
            try:
                with open(self.MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Reconstruct the memory store
                    memories = [MemoryItem(**item) for item in data.get('memories', [])]
                    
                    self.memory_store = CorporateMemory(
                        memories=memories,
                        total_memories=data.get('total_memories', 0),
                        type_distribution=data.get('type_distribution', {}),
                        importance_distribution=data.get('importance_distribution', {}),
                    )
            except Exception as e:
                # If loading fails, create new store
                print(f"Error loading memory from file: {e}")
                self.memory_store = CorporateMemory()
        else:
            self.memory_store = CorporateMemory()
    
    def _save_memory(self):
        """Save memory to persistent storage."""
        if self.memory_store is None:
            return
        
        self._ensure_data_directory()
        
        # Prepare data for serialization
        data = {
            "memories": [self._serialize_memory_item(m) for m in self.memory_store.memories],
            "total_memories": self.memory_store.total_memories,
            "type_distribution": self.memory_store.type_distribution,
            "importance_distribution": self.memory_store.importance_distribution,
            "last_updated": self.memory_store.last_updated.isoformat(),
        }
        
        with open(self.MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    @staticmethod
    def _serialize_memory_item(item: MemoryItem) -> Dict:
        """Serialize a memory item for JSON storage."""
        return {
            "memory_id": item.memory_id,
            "item_type": item.item_type.value,
            "timestamp": item.timestamp.isoformat(),
            "title": item.title,
            "description": item.description,
            "context": item.context,
            "related_entity_id": item.related_entity_id,
            "related_entity_type": item.related_entity_type,
            "importance": item.importance.value,
            "impact_score": item.impact_score,
            "access_count": item.access_count,
            "last_accessed": item.last_accessed.isoformat() if item.last_accessed else None,
            "tags": item.tags,
            "related_memory_ids": item.related_memory_ids,
        }
    
    def add_memory(
        self,
        item_type: MemoryItemType,
        title: str,
        description: str,
        context: Dict[str, Any],
        importance: Optional[MemoryImportance] = None,
        tags: Optional[List[str]] = None,
        related_entity_id: Optional[str] = None,
        related_entity_type: Optional[str] = None,
    ) -> MemoryItem:
        """
        Add a new memory to the store.
        
        Args:
            item_type: Type of memory
            title: Brief title
            description: Detailed description
            context: Contextual information
            importance: Optional importance level
            tags: Optional tags
            related_entity_id: Optional reference entity ID
            related_entity_type: Optional reference entity type
            
        Returns:
            MemoryItem: Created memory item
        """
        if self.memory_store is None:
            self.memory_store = CorporateMemory()
        
        memory_item = self.engine.add_memory(
            memory_store=self.memory_store,
            item_type=item_type,
            title=title,
            description=description,
            context=context,
            importance=importance,
            tags=tags,
            related_entity_id=related_entity_id,
            related_entity_type=related_entity_type,
        )
        
        self._save_memory()
        return memory_item
    
    def query_memories(self, query: MemoryQuery) -> MemoryQueryResult:
        """Query memories based on filter criteria."""
        if self.memory_store is None:
            return MemoryQueryResult(memories=[], total_count=0, query_time_ms=0.0)
        
        return self.engine.query_memories(self.memory_store, query)
    
    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryItem]:
        """Get a single memory by ID."""
        if self.memory_store is None:
            return None
        
        for memory in self.memory_store.memories:
            if memory.memory_id == memory_id:
                # Update access stats
                memory.access_count += 1
                memory.last_accessed = self._now()
                self._save_memory()
                return memory
        
        return None
    
    def get_memory_summary(self, max_recent: int = 5, max_critical: int = 3) -> CorporateMemorySummary:
        """Get a summary of corporate memory."""
        if self.memory_store is None:
            return CorporateMemorySummary()
        
        summary = self.engine.get_memory_summary(
            self.memory_store,
            max_recent=max_recent,
            max_critical=max_critical,
        )
        
        # Update last summarized
        self.memory_store.last_summarized = self._now()
        self._save_memory()
        
        return summary
    
    def get_all_memories(self, limit: int = 1000) -> List[MemoryItem]:
        """Get all memories with optional limit."""
        if self.memory_store is None:
            return []
        
        return sorted(
            self.memory_store.memories[:limit],
            key=lambda x: x.timestamp,
            reverse=True
        )
    
    def get_memories_by_type(self, item_type: MemoryItemType, limit: int = 100) -> List[MemoryItem]:
        """Get all memories of a specific type."""
        if self.memory_store is None:
            return []
        
        memories = [m for m in self.memory_store.memories if m.item_type == item_type]
        
        return sorted(
            memories[:limit],
            key=lambda x: x.timestamp,
            reverse=True
        )
    
    def export_memory_markdown(self, memory_id: Optional[str] = None) -> str:
        """
        Export memory as markdown.
        
        Args:
            memory_id: Specific memory ID to export, or None for all
            
        Returns:
            str: Markdown representation
        """
        if self.memory_store is None:
            return ""
        
        if memory_id:
            return self.engine.get_memory_markdown_export(self.memory_store, memory_id) or ""
        else:
            return self.engine.get_all_memories_markdown_export(self.memory_store)
    
    def record_intent_change(
        self,
        old_intent: Dict[str, Any],
        new_intent: Dict[str, Any],
        reason: str,
    ) -> MemoryItem:
        """Record an intent change."""
        if self.memory_store is None:
            self.memory_store = CorporateMemory()
        
        memory_item = self.engine.record_intent_change(
            self.memory_store, old_intent, new_intent, reason
        )
        
        self._save_memory()
        return memory_item
    
    def record_decision(
        self,
        decision_id: str,
        decision_desc: str,
        reasoning: str,
        supporting_roles: List[str],
        opposing_roles: List[str],
    ) -> MemoryItem:
        """Record an executive decision."""
        if self.memory_store is None:
            self.memory_store = CorporateMemory()
        
        memory_item = self.engine.record_decision(
            self.memory_store, decision_id, decision_desc, reasoning, supporting_roles, opposing_roles
        )
        
        self._save_memory()
        return memory_item
    
    def record_consciousness_evolution(
        self,
        old_phase: str,
        new_phase: str,
        milestone: str,
    ) -> MemoryItem:
        """Record consciousness evolution."""
        if self.memory_store is None:
            self.memory_store = CorporateMemory()
        
        memory_item = self.engine.record_consciousness_evolution(
            self.memory_store, old_phase, new_phase, milestone
        )
        
        self._save_memory()
        return memory_item
    
    @staticmethod
    def _now():
        """Get current UTC time."""
        from datetime import datetime
        return datetime.utcnow()
