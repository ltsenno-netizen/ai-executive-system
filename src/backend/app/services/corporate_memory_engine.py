"""
Corporate Memory Engine
========================

Core engine for memory operations including storage, retrieval, summarization,
and time-decay weighted importance computation.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import math

from ..models.corporate_memory_model import (
    MemoryItem,
    MemoryItemType,
    MemoryImportance,
    CorporateMemory,
    MemoryQuery,
    MemoryQueryResult,
    CorporateMemorySummary,
)


class CorporateMemoryEngine:
    """Engine for managing corporate memory operations."""
    
    # Time decay constants
    DECAY_HALF_LIFE_DAYS = 90  # Half-life for memory decay
    RECENCY_BOOST = 0.2  # Boost factor for recent memories
    
    # Importance weights
    IMPORTANCE_WEIGHTS = {
        MemoryImportance.LOW: 0.25,
        MemoryImportance.MEDIUM: 0.5,
        MemoryImportance.HIGH: 0.75,
        MemoryImportance.CRITICAL: 1.0,
    }
    
    # Type importance defaults
    TYPE_DEFAULT_IMPORTANCE = {
        MemoryItemType.INTENT_CHANGE: MemoryImportance.HIGH,
        MemoryItemType.DECISION: MemoryImportance.HIGH,
        MemoryItemType.CONSCIOUSNESS_EVOLUTION: MemoryImportance.HIGH,
        MemoryItemType.FRONTIER_UPDATE: MemoryImportance.MEDIUM,
        MemoryItemType.NARRATIVE_GENERATED: MemoryImportance.LOW,
        MemoryItemType.ENVIRONMENT_EVENT: MemoryImportance.MEDIUM,
        MemoryItemType.CULTURE_SHIFT: MemoryImportance.MEDIUM,
        MemoryItemType.CRISIS_EVENT: MemoryImportance.CRITICAL,
        MemoryItemType.MILESTONE_ACHIEVED: MemoryImportance.HIGH,
        MemoryItemType.LEARNING_RECORDED: MemoryImportance.MEDIUM,
    }

    @staticmethod
    def add_memory(
        memory_store: CorporateMemory,
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
        Add a new memory to the corporate memory store.
        
        Args:
            memory_store: Corporate memory container
            item_type: Type of memory
            title: Brief title
            description: Detailed description
            context: Contextual information
            importance: Optional importance level (auto-determined if not provided)
            tags: Optional tags for categorization
            related_entity_id: Optional reference to related entity
            related_entity_type: Optional type of related entity
            
        Returns:
            MemoryItem: Created memory item
        """
        # Determine importance if not provided
        if importance is None:
            importance = CorporateMemoryEngine.TYPE_DEFAULT_IMPORTANCE.get(
                item_type, MemoryImportance.MEDIUM
            )
        
        # Create memory item
        memory_item = MemoryItem(
            item_type=item_type,
            title=title,
            description=description,
            context=context,
            importance=importance,
            tags=tags or [],
            related_entity_id=related_entity_id,
            related_entity_type=related_entity_type,
        )
        
        # Add to store
        memory_store.memories.append(memory_item)
        
        # Update index
        memory_store.index[memory_item.memory_id] = {
            "memory_id": memory_item.memory_id,
            "item_type": memory_item.item_type,
            "timestamp": memory_item.timestamp,
            "title": memory_item.title,
            "importance": memory_item.importance,
            "tags": memory_item.tags,
            "impact_score": memory_item.impact_score,
        }
        
        # Update statistics
        memory_store.total_memories += 1
        type_key = item_type.value
        memory_store.type_distribution[type_key] = memory_store.type_distribution.get(type_key, 0) + 1
        imp_key = importance.value
        memory_store.importance_distribution[imp_key] = memory_store.importance_distribution.get(imp_key, 0) + 1
        
        # Update last modified
        memory_store.last_updated = datetime.utcnow()
        
        return memory_item

    @staticmethod
    def query_memories(
        memory_store: CorporateMemory,
        query: MemoryQuery,
    ) -> MemoryQueryResult:
        """
        Query memories based on filter criteria.
        
        Args:
            memory_store: Corporate memory container
            query: Query parameters
            
        Returns:
            MemoryQueryResult: Matching memories with metadata
        """
        start_time = datetime.utcnow()
        matching_memories = []
        
        for memory in memory_store.memories:
            # Apply filters
            if query.item_types and memory.item_type not in query.item_types:
                continue
            
            if query.importance_levels and memory.importance not in query.importance_levels:
                continue
            
            if query.start_date and memory.timestamp < query.start_date:
                continue
            
            if query.end_date and memory.timestamp > query.end_date:
                continue
            
            if query.min_impact_score and memory.impact_score < query.min_impact_score:
                continue
            
            if query.tags:
                # All tags must be present
                if not all(tag in memory.tags for tag in query.tags):
                    continue
            
            if query.search_text:
                search_lower = query.search_text.lower()
                if search_lower not in memory.title.lower() and search_lower not in memory.description.lower():
                    continue
            
            matching_memories.append(memory)
        
        # Sort by timestamp descending
        matching_memories.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply offset and limit
        paginated_memories = matching_memories[query.offset : query.offset + query.limit]
        
        # Calculate query time
        query_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return MemoryQueryResult(
            memories=paginated_memories,
            total_count=len(matching_memories),
            query_time_ms=query_time_ms,
        )

    @staticmethod
    def compute_effective_weight(
        memory: MemoryItem,
        current_time: Optional[datetime] = None,
    ) -> float:
        """
        Compute effective weight of a memory considering time decay and importance.
        
        Args:
            memory: Memory item
            current_time: Current time (defaults to now)
            
        Returns:
            float: Effective weight (0.0 to 1.0)
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Base weight from importance
        importance_weight = CorporateMemoryEngine.IMPORTANCE_WEIGHTS.get(
            memory.importance, 0.5
        )
        
        # Time decay
        age_days = (current_time - memory.timestamp).days
        decay_factor = math.exp(-0.693 * (age_days / CorporateMemoryEngine.DECAY_HALF_LIFE_DAYS))
        
        # Recency boost
        if age_days < 7:
            recency_factor = 1.0 + CorporateMemoryEngine.RECENCY_BOOST
        else:
            recency_factor = 1.0
        
        # Access frequency boost
        access_factor = 1.0 + (0.01 * memory.access_count)
        
        # Combine factors
        effective_weight = importance_weight * decay_factor * recency_factor * access_factor
        
        # Clamp to 0-1
        return min(1.0, max(0.0, effective_weight))

    @staticmethod
    def get_memory_summary(
        memory_store: CorporateMemory,
        max_recent: int = 5,
        max_critical: int = 3,
    ) -> CorporateMemorySummary:
        """
        Generate a summary of corporate memory for dashboards.
        
        Args:
            memory_store: Corporate memory container
            max_recent: Maximum recent memories to include
            max_critical: Maximum critical memories to include
            
        Returns:
            CorporateMemorySummary: Summary of corporate memory
        """
        # Get recent memories
        recent = sorted(memory_store.memories, key=lambda x: x.timestamp, reverse=True)[:max_recent]
        
        # Get critical memories
        critical = [
            m for m in memory_store.memories
            if m.importance == MemoryImportance.CRITICAL
        ]
        critical.sort(key=lambda x: x.timestamp, reverse=True)
        critical = critical[:max_critical]
        
        # Count memories by period
        now = datetime.utcnow()
        month_ago = now - timedelta(days=30)
        quarter_ago = now - timedelta(days=90)
        
        memories_this_month = sum(1 for m in memory_store.memories if m.timestamp >= month_ago)
        memories_this_quarter = sum(1 for m in memory_store.memories if m.timestamp >= quarter_ago)
        
        # Extract intent evolution
        intent_memories = [
            m for m in memory_store.memories
            if m.item_type == MemoryItemType.INTENT_CHANGE
        ]
        intent_evolution = [f"{m.timestamp.strftime('%Y-%m-%d')}: {m.title}" for m in intent_memories[-5:]]
        
        # Extract consciousness phases
        consciousness_memories = [
            m for m in memory_store.memories
            if m.item_type in [MemoryItemType.CONSCIOUSNESS_STATE, MemoryItemType.CONSCIOUSNESS_EVOLUTION]
        ]
        consciousness_phases = [f"{m.timestamp.strftime('%Y-%m-%d')}: {m.title}" for m in consciousness_memories[-5:]]
        
        # Top impactful events
        impactful = sorted(
            memory_store.memories,
            key=lambda x: CorporateMemoryEngine.compute_effective_weight(x),
            reverse=True
        )[:5]
        top_impactful = [
            {
                "title": m.title,
                "type": m.item_type.value,
                "impact_score": m.impact_score,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in impactful
        ]
        
        return CorporateMemorySummary(
            total_memories=memory_store.total_memories,
            memory_types=memory_store.type_distribution,
            importance_distribution=memory_store.importance_distribution,
            recent_memories=recent,
            critical_memories=critical,
            intent_evolution=intent_evolution,
            consciousness_phases=consciousness_phases,
            top_impactful_events=top_impactful,
            memories_this_month=memories_this_month,
            memories_this_quarter=memories_this_quarter,
        )

    @staticmethod
    def get_memory_markdown_export(
        memory_store: CorporateMemory,
        memory_id: str,
    ) -> Optional[str]:
        """
        Export a single memory as markdown.
        
        Args:
            memory_store: Corporate memory container
            memory_id: Memory ID to export
            
        Returns:
            str: Markdown representation of the memory, or None if not found
        """
        memory = next((m for m in memory_store.memories if m.memory_id == memory_id), None)
        if not memory:
            return None
        
        markdown = f"""# {memory.title}

**Type:** {memory.item_type.value}
**Timestamp:** {memory.timestamp.isoformat()}
**Importance:** {memory.importance.value}
**Impact Score:** {memory.impact_score:.2f}

## Description

{memory.description}

## Context

"""
        for key, value in memory.context.items():
            markdown += f"- **{key}:** {value}\n"
        
        if memory.tags:
            markdown += f"\n## Tags\n\n{', '.join(memory.tags)}\n"
        
        if memory.related_memory_ids:
            markdown += f"\n## Related Memories\n\n{', '.join(memory.related_memory_ids)}\n"
        
        return markdown

    @staticmethod
    def get_all_memories_markdown_export(
        memory_store: CorporateMemory,
    ) -> str:
        """
        Export all memories as markdown.
        
        Args:
            memory_store: Corporate memory container
            
        Returns:
            str: Markdown representation of all memories
        """
        markdown = f"# Corporate Memory Export\n\n**Generated:** {datetime.utcnow().isoformat()}\n\n"
        markdown += f"**Total Memories:** {memory_store.total_memories}\n\n"
        
        # Group by type
        memories_by_type = {}
        for memory in memory_store.memories:
            type_key = memory.item_type.value
            if type_key not in memories_by_type:
                memories_by_type[type_key] = []
            memories_by_type[type_key].append(memory)
        
        for item_type, memories in sorted(memories_by_type.items()):
            markdown += f"\n## {item_type}\n\n"
            for memory in sorted(memories, key=lambda x: x.timestamp, reverse=True):
                markdown += f"### {memory.title}\n"
                markdown += f"- **Date:** {memory.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                markdown += f"- **Importance:** {memory.importance.value}\n"
                markdown += f"- **Impact:** {memory.impact_score:.2f}\n\n"
        
        return markdown

    @staticmethod
    def record_intent_change(
        memory_store: CorporateMemory,
        old_intent: Dict[str, Any],
        new_intent: Dict[str, Any],
        reason: str,
    ) -> MemoryItem:
        """Helper to record an intent change."""
        changes = {
            "old": old_intent,
            "new": new_intent,
            "reason": reason,
        }
        
        return CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.INTENT_CHANGE,
            title=f"Intent Updated: {reason}",
            description=f"Corporate intent was updated. Reason: {reason}",
            context=changes,
            importance=MemoryImportance.HIGH,
        )

    @staticmethod
    def record_decision(
        memory_store: CorporateMemory,
        decision_id: str,
        decision_desc: str,
        reasoning: str,
        supporting_roles: List[str],
        opposing_roles: List[str],
    ) -> MemoryItem:
        """Helper to record an executive decision."""
        context = {
            "decision_id": decision_id,
            "supporting_roles": supporting_roles,
            "opposing_roles": opposing_roles,
            "reasoning": reasoning,
        }
        
        return CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.DECISION,
            title=f"Decision: {decision_desc}",
            description=f"Executive decision made: {decision_desc}. Reasoning: {reasoning}",
            context=context,
            importance=MemoryImportance.HIGH,
            tags=["decision", "executive"],
        )

    @staticmethod
    def record_consciousness_evolution(
        memory_store: CorporateMemory,
        old_phase: str,
        new_phase: str,
        milestone: str,
    ) -> MemoryItem:
        """Helper to record consciousness evolution."""
        context = {
            "old_phase": old_phase,
            "new_phase": new_phase,
            "milestone": milestone,
        }
        
        return CorporateMemoryEngine.add_memory(
            memory_store=memory_store,
            item_type=MemoryItemType.CONSCIOUSNESS_EVOLUTION,
            title=f"Consciousness Evolution: {old_phase} → {new_phase}",
            description=f"Organizational consciousness evolved from {old_phase} to {new_phase}. Milestone: {milestone}",
            context=context,
            importance=MemoryImportance.HIGH,
            tags=["consciousness", "evolution", "milestone"],
        )
