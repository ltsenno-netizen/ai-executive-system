# Enterprise Autopilot Overview

This document describes the Step AM Enterprise Autopilot implementation.

## Purpose

Enterprise Autopilot is a periodic orchestration engine that executes a guided cycle across existing AI systems to align perception, evaluation, prediction, comparison, strategy, execution, and learning.

## Architecture

- `src/backend/app/models/enterprise_autopilot_model.py`
  - `AutopilotCyclePhase`
  - `AutopilotPhaseResult`
  - `AutopilotCycleResult`
  - `AutopilotSummary`

- `src/backend/app/services/enterprise_autopilot_engine.py`
  - Orchestrates phase execution
  - Calls existing services for consciousness, environment, scenario simulation, meta-cognition, multi-company comparison, and strategy engine v2
  - Logs decisions and synthesizes cycle metrics

- `src/backend/app/services/enterprise_autopilot_repository.py`
  - Persists cycle history under `data/enterprise_autopilot/cycle_history.json`

- `src/backend/app/services/enterprise_autopilot_service.py`
  - Runs cycles, saves history, and records corporate memory events

- `src/backend/app/routes/enterprise_autopilot.py`
  - REST endpoints to run cycles, get latest result, and retrieve history

## Dashboard Integration

- Extended `ExecutiveDashboard` with `enterprise_autopilot_summary`
- Added `_aggregate_enterprise_autopilot_summary` to `ExecutiveDashboardService`

## API Endpoints

- `POST /api/enterprise-autopilot/run`
- `GET /api/enterprise-autopilot/latest`
- `GET /api/enterprise-autopilot/history?limit=5`

## Validation

- New test coverage in `tests/test_enterprise_autopilot_engine.py`
- Service tests in `tests/test_enterprise_autopilot_service.py`
- API tests in `tests/test_enterprise_autopilot_api.py`
- Dashboard integration test in `tests/test_enterprise_autopilot_dashboard_summary.py`
