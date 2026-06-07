# Future Scenario Simulation Overview

## Step AJ: Future Scenario Simulation Engine

This module defines the new future scenario simulation capability for Step AJ. It extends the existing scenario planning infrastructure with:

- Formal simulation definitions for future-facing scenario models
- Environment-driven projections with regulatory and supply chain stress factors
- Culture and corporate consciousness evolution projections
- Financial impact summaries and scenario confidence estimates
- Contingency recommendations and strategic implication outputs

## Core components

- `src/backend/app/models/scenario_simulation_model.py`
  - Defines `ScenarioSimulationDefinition` and `ScenarioSimulationResult`
  - Captures both operational drivers and strategic forecasts

- `src/backend/app/services/scenario_simulation_engine.py`
  - Builds executable simulation logic for future scenarios
  - Projects environment, culture, consciousness evolution, and financial impacts
  - Produces scenario scoring and risk/opportunity assessments

- `src/backend/app/services/scenario_simulation_service.py`
  - Orchestrates simulation execution and persistence
  - Loads baseline state from culture, environment, consciousness evolution, and finance services
  - Stores simulation outputs under `/data/scenario_simulations/`

- `src/backend/app/routes/scenario_simulation.py`
  - Provides REST endpoints for running and retrieving simulation outputs
  - Supports summary preview for dashboard integration

- `src/backend/app/services/executive_dashboard_service.py`
  - Integrates future scenario simulation preview into the executive dashboard

## API Endpoints

- `POST /api/scenario-simulations/run`
- `GET /api/scenario-simulations/latest`
- `GET /api/scenario-simulations/{scenario_type}`
- `GET /api/scenario-simulations/preview`

## Data persistence

Simulation results are stored as JSON files in `/data/scenario_simulations/`, one file per scenario type:
- `baseline.json`
- `optimistic.json`
- `pessimistic.json`
- `tech_boom.json`
- `recession.json`

## Dashboard integration

The executive dashboard can now surface a condensed preview of the latest future scenario simulation, including:
- `scenario_type`
- `risk_assessment`
- `opportunity_assessment`
- `confidence`
- `financial_impact_summary`
- `strategic_implications`
- `contingency_recommendations`
