"""
Corporate Memory Model
======================

Models for the corporate memory system that maintains historical records
of decisions, narratives, consciousness states, evolution, intents, frontier
changes, culture shifts, and environmental events.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryItemType(str, Enum):
    """Types of memories that can be stored."""
    INTENT_CHANGE = "INTENT_CHANGE"  # Corporate intent update
    DECISION = "DECISION"  # Executive decision made
    FRONTIER_UPDATE = "FRONTIER_UPDATE"  # Frontier optimization status
    CONSCIOUSNESS_STATE = "CONSCIOUSNESS_STATE"  # Consciousness phase/state
    CONSCIOUSNESS_EVOLUTION = "CONSCIOUSNESS_EVOLUTION"  # Evolution milestone
    NARRATIVE_GENERATED = "NARRATIVE_GENERATED"  # Narrative created for audience
    ENVIRONMENT_EVENT = "ENVIRONMENT_EVENT"  # External environment change
    CULTURE_SHIFT = "CULTURE_SHIFT"  # Culture profile update
    STRATEGY_EXECUTED = "STRATEGY_EXECUTED"  # Strategy executed
    PERFORMANCE_METRIC = "PERFORMANCE_METRIC"  # Performance data
    AGENT_INTERACTION = "AGENT_INTERACTION"  # Executive agent action
    QUARTERLY_REVIEW = "QUARTERLY_REVIEW"  # Quarterly review/assessment
    ANNUAL_REVIEW = "ANNUAL_REVIEW"  # Annual review/assessment
    CRISIS_EVENT = "CRISIS_EVENT"  # Crisis or critical event
    OPPORTUNITY_IDENTIFIED = "OPPORTUNITY_IDENTIFIED"  # Opportunity spotted
    RISK_MATERIALIZED = "RISK_MATERIALIZED"  # Risk that materialized
    MILESTONE_ACHIEVED = "MILESTONE_ACHIEVED"  # Important milestone
    LEARNING_RECORDED = "LEARNING_RECORDED"  # Organizational learning
    SYSTEM_EVENT = "SYSTEM_EVENT"  # System-level event
    META_COGNITION = "META_COGNITION"  # Meta-Cognition assessment
    EXECUTIVE_SIMULATION = "EXECUTIVE_SIMULATION"  # Executive simulation meeting result
    AUTOPILOT_CYCLE = "AUTOPILOT_CYCLE"  # Enterprise Autopilot cycle


class MemoryImportance(str, Enum):
    """Importance levels for memories."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MemoryItem(BaseModel):
    """Individual memory record with context and metadata."""
    
    memory_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique memory identifier")
    item_type: MemoryItemType = Field(..., description="Type of memory")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the memory occurred")
    
    # Content
    title: str = Field(..., description="Brief title of the memory")
    description: str = Field(..., description="Detailed description of what happened")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual information")
    
    # Reference data
    related_entity_id: Optional[str] = Field(None, description="ID of related entity (decision, narrative, etc)")
    related_entity_type: Optional[str] = Field(None, description="Type of related entity")
    
    # Importance and impact
    importance: MemoryImportance = Field(default=MemoryImportance.MEDIUM, description="Importance of this memory")
    impact_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Estimated impact on future decisions")
    
    # Time decay tracking
    access_count: int = Field(default=0, description="Number of times this memory was accessed")
    last_accessed: Optional[datetime] = Field(None, description="Last time this memory was accessed")
    
    # Tags for categorization
    tags: List[str] = Field(default_factory=list, description="Tags for filtering and searching")
    
    # Connection to other memories
    related_memory_ids: List[str] = Field(default_factory=list, description="IDs of related memories")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class CorporateMemoryIndexEntry(BaseModel):
    """Index entry for efficient memory lookup."""
    memory_id: str
    item_type: MemoryItemType
    timestamp: datetime
    title: str
    importance: MemoryImportance
    tags: List[str]
    impact_score: float


class CorporateMemory(BaseModel):
    """Complete corporate memory container."""
    
    memories: List[MemoryItem] = Field(default_factory=list, description="All stored memories")
    index: Dict[str, CorporateMemoryIndexEntry] = Field(default_factory=dict, description="Index for quick lookup")
    
    # Aggregate statistics
    total_memories: int = Field(default=0, description="Total number of memories stored")
    type_distribution: Dict[str, int] = Field(default_factory=dict, description="Count by memory type")
    importance_distribution: Dict[str, int] = Field(default_factory=dict, description="Count by importance")
    
    # Historical trends
    intent_history: List[Dict[str, Any]] = Field(default_factory=list, description="Intent changes over time")
    consciousness_history: List[Dict[str, Any]] = Field(default_factory=list, description="Consciousness evolution")
    frontier_history: List[Dict[str, float]] = Field(default_factory=list, description="Frontier scores over time")
    culture_history: List[Dict[str, Any]] = Field(default_factory=list, description="Culture profile changes")
    
    # Last update
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last memory update timestamp")
    last_summarized: Optional[datetime] = Field(None, description="Last summary computation")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class MemoryQuery(BaseModel):
    """Query parameters for memory retrieval."""
    
    item_types: Optional[List[MemoryItemType]] = Field(None, description="Filter by memory types")
    importance_levels: Optional[List[MemoryImportance]] = Field(None, description="Filter by importance")
    start_date: Optional[datetime] = Field(None, description="Start date for time range")
    end_date: Optional[datetime] = Field(None, description="End date for time range")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (AND logic)")
    search_text: Optional[str] = Field(None, description="Full-text search in description/title")
    min_impact_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum impact score")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class MemoryQueryResult(BaseModel):
    """Results from a memory query."""
    
    memories: List[MemoryItem] = Field(..., description="Matching memories")
    total_count: int = Field(..., description="Total number of matches")
    query_time_ms: float = Field(..., description="Query execution time in milliseconds")


class CorporateMemorySummary(BaseModel):
    """Summary of corporate memory for dashboard."""
    
    total_memories: int = Field(default=0, description="Total memories stored")
    memory_types: Dict[str, int] = Field(default_factory=dict, description="Distribution by type")
    importance_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribution by importance")
    
    # Recent memories
    recent_memories: List[MemoryItem] = Field(default_factory=list, description="5 most recent memories")
    critical_memories: List[MemoryItem] = Field(default_factory=list, description="Critical memories")
    
    # Trends
    intent_evolution: List[str] = Field(default_factory=list, description="Recent intent changes")
    consciousness_phases: List[str] = Field(default_factory=list, description="Consciousness phases over time")
    top_impactful_events: List[Dict[str, Any]] = Field(default_factory=list, description="Most impactful memories")
    
    # Temporal stats
    memories_this_month: int = Field(default=0, description="Memories recorded this month")
    memories_this_quarter: int = Field(default=0, description="Memories recorded this quarter")
    
    # Last update
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Summary generation time")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
