# Executive Meeting Debate

## Strategic Debate Engine

The debate flow consists of:

1. Agenda presentation
2. Opening statements from each AI executive agent
3. Cross-discussion between financial, operational, market, and organizational topics
4. Consensus and divergence summaries

## Debate Outputs

- `opening_statements`: agent-by-agent narrative positions
- `cross_discussion`: shared talking points and risk debates
- `consensus`: aligned strategic direction
- `divergence`: remaining tradeoff disagreements

## Data Flow

- `ExecutiveMeetingService` calls the debate engine after agenda generation.
- Debate output is saved into `ExecutiveMeetingState`.
- The summary is available through API and dashboard aggregation.
