# Executive Meeting Agents

## AI Executive Roles

The meeting simulation now includes four AI executive roles:

- CFO: cash, investment, risk, capital policy
- COO: execution capacity, project load, operational risk
- CMO: market timing, customer acquisition, campaign effectiveness
- CHRO: organizational health, staffing, workload and retention

## Role Behavior

Each agent:

- Reviews the meeting agenda
- Generates an opening statement based on their domain
- Highlights risks, opportunities, and tradeoffs
- Contributes to the strategic debate

## Implementation

- `ai_executive_agents.py` defines executive role focus and concern maps.
- `executive_meeting_engine.py` builds agent statements from agenda items.
- Each agent is represented in the meeting state for dashboard and narrative consumption.
