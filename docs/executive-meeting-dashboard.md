# Executive Meeting Dashboard

## Dashboard Summary Panel

The executive dashboard now includes an Executive Meeting Summary panel with:

- Current meeting agenda count
- Selected decision option
- Count of approved / rejected / modified / held items
- Next month projection highlight
- Risk level derived from the selected option

## Integration

- `ExecutiveDashboardService` aggregates the latest executed meeting state.
- `ExecutiveMeetingSummary` now includes:
  - `selected_option_id`
  - `selected_option_label`
  - `meeting_risk_level`
- `ExecutiveDashboard` now includes `meeting_timeline`, which tracks the last 6 months of executive decisions.

## Executive Meeting Timeline

- Shows the last 6 months of choice history.
- Each timeline item includes:
  - month
  - selected option id and label
  - approved / rejected / modified / held counts
  - next month projection highlight
  - meeting risk level

## Visualization

The dashboard can show:

- AI agent consensus and divergence
- Chosen CEO option
- Expected impact on revenue, profit, and margin
- Risk classification: High / Medium / Low
