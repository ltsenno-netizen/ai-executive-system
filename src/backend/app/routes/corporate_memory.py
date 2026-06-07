"""
Corporate Memory API Routes
===========================

REST endpoints for corporate memory operations.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..models.corporate_memory_model import (
    MemoryItem,
    MemoryItemType,
    MemoryImportance,
    MemoryQuery,
    MemoryQueryResult,
    CorporateMemorySummary,
)
from ..services.corporate_memory_service import CorporateMemoryService

router = APIRouter(tags=["corporate-memory"])

# Lazy load service
_service: Optional[CorporateMemoryService] = None


def get_service() -> CorporateMemoryService:
    """Get or create the service."""
    global _service
    if _service is None:
        _service = CorporateMemoryService()
    return _service


# Request models for API
class AddMemoryRequest(BaseModel):
    """Request to add a new memory."""
    item_type: str  # MemoryItemType value
    title: str
    description: str
    context: dict
    importance: Optional[str] = None  # MemoryImportance value
    tags: Optional[List[str]] = None
    related_entity_id: Optional[str] = None
    related_entity_type: Optional[str] = None


class MemoryQueryRequest(BaseModel):
    """Request to query memories."""
    item_types: Optional[List[str]] = None
    importance_levels: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    min_impact_score: Optional[float] = None
    tags: Optional[List[str]] = None
    search_text: Optional[str] = None
    limit: int = 50
    offset: int = 0


# Endpoints
@router.post("/memory/add", response_model=MemoryItem, tags=["memory"])
def add_memory(request: AddMemoryRequest):
    """
    Add a new memory to corporate memory store.
    
    Args:
        request: Memory details to add
        
    Returns:
        MemoryItem: Created memory item
    """
    service = get_service()
    
    try:
        item_type = MemoryItemType(request.item_type.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid item_type: {request.item_type}"
        )
    
    importance = None
    if request.importance:
        try:
            importance = MemoryImportance(request.importance.upper())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid importance: {request.importance}"
            )
    
    memory_item = service.add_memory(
        item_type=item_type,
        title=request.title,
        description=request.description,
        context=request.context,
        importance=importance,
        tags=request.tags,
        related_entity_id=request.related_entity_id,
        related_entity_type=request.related_entity_type,
    )
    
    return memory_item


@router.get("/memory/all", response_model=List[MemoryItem], tags=["memory"])
def get_all_memories(limit: int = Query(100, ge=1, le=1000)):
    """Get all memories with optional limit."""
    service = get_service()
    return service.get_all_memories(limit=limit)


@router.get("/memory/type/{item_type}", response_model=List[MemoryItem], tags=["memory"])
def get_memories_by_type(item_type: str, limit: int = Query(100, ge=1, le=1000)):
    """Get all memories of a specific type."""
    service = get_service()
    
    try:
        memory_type = MemoryItemType(item_type.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid item_type: {item_type}"
        )
    
    return service.get_memories_by_type(memory_type, limit=limit)


@router.post("/memory/query", response_model=MemoryQueryResult, tags=["memory"])
def query_memories(request: MemoryQueryRequest):
    """Query memories with advanced filters."""
    service = get_service()
    
    # Convert string enums to actual enums
    item_types = None
    if request.item_types:
        try:
            item_types = [MemoryItemType(t.upper()) for t in request.item_types]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid item_type: {str(e)}")
    
    importance_levels = None
    if request.importance_levels:
        try:
            importance_levels = [MemoryImportance(i.upper()) for i in request.importance_levels]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid importance: {str(e)}")
    
    # Build query
    from datetime import datetime
    
    start_date = None
    if request.start_date:
        try:
            start_date = datetime.fromisoformat(request.start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format (use ISO 8601)")
    
    end_date = None
    if request.end_date:
        try:
            end_date = datetime.fromisoformat(request.end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format (use ISO 8601)")
    
    query = MemoryQuery(
        item_types=item_types,
        importance_levels=importance_levels,
        start_date=start_date,
        end_date=end_date,
        min_impact_score=request.min_impact_score,
        tags=request.tags,
        search_text=request.search_text,
        limit=request.limit,
        offset=request.offset,
    )
    
    return service.query_memories(query)


@router.get("/memory/summary", response_model=CorporateMemorySummary, tags=["memory"])
def get_memory_summary(
    max_recent: int = Query(5, ge=1, le=20),
    max_critical: int = Query(3, ge=1, le=10)
):
    """Get a summary of corporate memory for dashboards."""
    service = get_service()
    return service.get_memory_summary(max_recent=max_recent, max_critical=max_critical)


@router.get("/memory/{memory_id}/markdown", response_model=dict, tags=["memory"])
def export_memory_markdown(memory_id: str):
    """Export a single memory as markdown."""
    service = get_service()
    markdown = service.export_memory_markdown(memory_id=memory_id)
    
    if not markdown:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return {"markdown": markdown}


@router.get("/memory/markdown/all", response_model=dict, tags=["memory"])
def export_all_memories_markdown():
    """Export all memories as markdown."""
    service = get_service()
    markdown = service.export_memory_markdown()
    
    return {"markdown": markdown}


@router.get("/memory/intent-changes", response_model=List[MemoryItem], tags=["memory"])
def get_intent_changes(limit: int = Query(20, ge=1, le=100)):
    """Get all recorded intent changes."""
    service = get_service()
    return service.get_memories_by_type(MemoryItemType.INTENT_CHANGE, limit=limit)


@router.get("/memory/decisions", response_model=List[MemoryItem], tags=["memory"])
def get_decisions(limit: int = Query(20, ge=1, le=100)):
    """Get all recorded decisions."""
    service = get_service()
    return service.get_memories_by_type(MemoryItemType.DECISION, limit=limit)


@router.get("/memory/consciousness-events", response_model=List[MemoryItem], tags=["memory"])
def get_consciousness_events(limit: int = Query(20, ge=1, le=100)):
    """Get consciousness-related events."""
    service = get_service()
    
    consciousness_state_memories = service.get_memories_by_type(
        MemoryItemType.CONSCIOUSNESS_STATE, limit=limit // 2
    )
    consciousness_evolution_memories = service.get_memories_by_type(
        MemoryItemType.CONSCIOUSNESS_EVOLUTION, limit=limit // 2
    )
    
    combined = consciousness_state_memories + consciousness_evolution_memories
    combined.sort(key=lambda x: x.timestamp, reverse=True)
    
    return combined[:limit]


@router.get("/memory/types", response_model=dict, tags=["memory"])
def get_memory_types():
    """Get all available memory types."""
    return {
        "types": [t.value for t in MemoryItemType],
    }


@router.get("/memory/importances", response_model=dict, tags=["memory"])
def get_importance_levels():
    """Get all importance levels."""
    return {
        "levels": [i.value for i in MemoryImportance],
    }


@router.get("/memory/metrics", response_model=dict, tags=["memory"])
def get_memory_metrics():
    """Get memory system metrics."""
    service = get_service()
    summary = service.get_memory_summary()
    
    return {
        "total_memories": summary.total_memories,
        "memory_types": summary.memory_types,
        "importance_distribution": summary.importance_distribution,
        "memories_this_month": summary.memories_this_month,
        "memories_this_quarter": summary.memories_this_quarter,
    }


@router.get("/memory/{memory_id}", response_model=MemoryItem, tags=["memory"])
def get_memory(memory_id: str):
    """Get a specific memory by ID."""
    service = get_service()
    memory = service.get_memory_by_id(memory_id)
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return memory
