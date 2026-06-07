# Corporate Memory Overview

## Purpose

The corporate memory layer makes the enterprise system a remembering entity. It captures, stores, and surfaces historical knowledge across decisions, narratives, intent changes, culture shifts, environment events, consciousness evolution, and other strategic milestones.

This layer enables:
- persistent historical memory across restarts
- time-decay weighted importance for relevance
- advanced query and filtering
- dashboard-ready summaries
- API access for other system components

## Architecture

### Key Components

- `src/backend/app/models/corporate_memory_model.py`
  - Defines memory data structures and query payloads.
  - Models include:
    - `MemoryItem`
    - `CorporateMemory`
    - `MemoryQuery`
    - `MemoryQueryResult`
    - `CorporateMemorySummary`

- `src/backend/app/services/corporate_memory_engine.py`
  - Implements business logic for memory operations.
  - Handles:
    - adding new memories
    - querying with filters
    - effective weight calculation using decay
    - memory summarization
    - markdown export
    - helper methods for intent, decision, and consciousness events

- `src/backend/app/services/corporate_memory_service.py`
  - Manages persistence to `data/corporate_memory/memory.json`.
  - Provides high-level APIs for:
    - adding memories
    - retrieving memory records
    - exporting markdown
    - summarization
    - memory statistics

- `src/backend/app/routes/corporate_memory.py`
  - Exposes REST endpoints for memory operations.
  - Supports:
    - POST `/api/memory/add`
    - GET `/api/memory/all`
    - GET `/api/memory/{memory_id}`
    - GET `/api/memory/type/{item_type}`
    - POST `/api/memory/query`
    - GET `/api/memory/summary`
    - GET `/api/memory/markdown/all`
    - GET `/api/memory/{memory_id}/markdown`
    - metadata endpoints for types and importance levels

- `src/backend/app/services/executive_dashboard_service.py`
  - Integrates memory summaries into the executive dashboard.
  - Adds `corporate_memory_summary` to the dashboard model.

## Memory Structure

### MemoryItem

Each memory item includes:
- `memory_id`
- `item_type`
- `timestamp`
- `title`
- `description`
- `context`
- `related_entity_id`
- `related_entity_type`
- `importance`
- `impact_score`
- `access_count`
- `last_accessed`
- `tags`
- `related_memory_ids`

### MemoryItemType

Supported memory types include:
- `INTENT_CHANGE`
- `DECISION`
- `FRONTIER_UPDATE`
- `CONSCIOUSNESS_STATE`
- `CONSCIOUSNESS_EVOLUTION`
- `NARRATIVE_GENERATED`
- `ENVIRONMENT_EVENT`
- `CULTURE_SHIFT`
- `STRATEGY_EXECUTED`
- `PERFORMANCE_METRIC`
- `AGENT_INTERACTION`
- `QUARTERLY_REVIEW`
- `ANNUAL_REVIEW`
- `CRISIS_EVENT`
- `OPPORTUNITY_IDENTIFIED`
- `RISK_MATERIALIZED`
- `MILESTONE_ACHIEVED`
- `LEARNING_RECORDED`
- `SYSTEM_EVENT`

### MemoryImportance

Importance values are:
- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

## Time-Decay Weighting

The memory engine scores memories using:
- importance weight
- exponential decay over a 90-day half-life
- recency boost for memories within 7 days
- access count boost

This supports relevance ranking while preserving long-term history.

## Persistence

Memories are persisted to JSON in `data/corporate_memory/memory.json`.
The service serializes `MemoryItem` objects with:
- enum values saved as uppercase strings
- timestamps in ISO 8601 format
- context and metadata fields preserved

## API Usage

### Add memory

`POST /api/memory/add`

Request body:
```json
{
  "item_type": "decision",
  "title": "Approve new growth fund",
  "description": "Approved a new growth fund for Q3 initiatives.",
  "context": {"fund_size": 5000000},
  "importance": "high",
  "tags": ["strategy", "investment"]
}
```

### Query memories

`POST /api/memory/query`

Request body:
```json
{
  "item_types": ["decision", "crisis_event"],
  "importance_levels": ["high"],
  "tags": ["strategy"],
  "limit": 20,
  "offset": 0
}
```

### Export markdown

- `GET /api/memory/markdown/all`
- `GET /api/memory/{memory_id}/markdown`

### Dashboard summary

- `GET /api/memory/summary`

This summary is also included in the executive dashboard model as `corporate_memory_summary`.

## Dashboard Integration

Corporate memory is surfaced in the executive dashboard by:
- loading summaries from `CorporateMemoryService`
- injecting `corporate_memory_summary` into `ExecutiveDashboard`
- capturing trends such as intent evolution, consciousness phases, recent and critical memories

## Testing

The corporate memory layer is covered with tests in:
- `tests/test_corporate_memory_engine.py`
- `tests/test_corporate_memory_service.py`
- `tests/test_corporate_memory_api.py`
- `tests/test_dashboard_corporate_memory.py`

All new tests currently pass.
