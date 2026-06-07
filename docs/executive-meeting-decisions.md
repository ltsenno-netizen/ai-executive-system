# Executive Meeting Decision Options

## Decision Option Generator

The engine generates three comparable decision options:

- A: 攻めの投資継続
- B: 守りの投資抑制
- C: バランス型

Each option includes:

- `id`
- `label`
- `actions`
- `pros`
- `cons`

## API

- `GET /api/meeting/options?month={month}`
  - Returns A/B/C option definitions.
- `POST /api/meeting/decision`
  - Request: `{ month, option_id, ceo_comment }`
  - Response: updated meeting state, projection, and meeting minutes.

## Decision Reflection

- Selected option is stored in meeting state.
- The system applies category-based approval logic to agenda items.
- The selected option affects next month projections and dashboard risk evaluation.
