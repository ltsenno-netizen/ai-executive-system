# Corporate Strategy Engine 2.0 Overview

This document describes the new Corporate Strategy Engine 2.0 introduced as Step AL.

## Purpose

The engine generates an integrated corporate strategy report by combining:

- future scenario simulation outputs from Step AJ
- corporate intent and preferences from Step AA
- frontier optimization health from Step AD
- corporate consciousness insights from Step AE
- corporate memory context from the memory system

## Components

- `src/backend/app/models/strategy_engine_v2_model.py`
  - Defines report, directive, asset, and dashboard summary models.
- `src/backend/app/services/strategy_engine_v2.py`
  - Implements the integrated strategy report generator.
- `src/backend/app/services/strategy_engine_v2_service.py`
  - Orchestrates data retrieval, persistence, and markdown export.
- `src/backend/app/routes/strategy_engine_v2.py`
  - Exposes REST endpoints under `/api/strategy/v2`.

## API

- `POST /api/strategy/v2/run/{scenario_type}`
  - Generate or refresh a strategy report for the specified scenario.
- `GET /api/strategy/v2/latest/{scenario_type}`
  - Retrieve the latest saved report for a scenario.
- `GET /api/strategy/v2/latest`
  - Retrieve the most recent strategy report overall.
- `GET /api/strategy/v2/markdown/{scenario_type}`
  - Export a strategy report in markdown format.

## Dashboard Integration

A new `StrategyV2Summary` section is added to the executive dashboard summary.
It surfaces the most recent strategy report, alignment scores, resilience scores, and top recommended actions.

## Data Persistence

Reports are serialized to `data/strategy_engine_v2/{scenario_type}.json`.

## Notes

This engine intentionally uses existing services to avoid duplication and ensure consistency across model ecosystems.
