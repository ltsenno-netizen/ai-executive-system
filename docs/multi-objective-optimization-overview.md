# Multi-Objective Optimization Overview

## 概要 (Overview)

**Multi-Objective Optimization** is Phase Z of the autonomous enterprise system, extending single-objective decision-making with simultaneous optimization across four critical dimensions: **Growth**, **Profitability**, **Innovation**, and **Stability**.

### The Challenge

Enterprise decision-making rarely involves a single objective. Growth strategies may sacrifice profitability. Innovation initiatives may increase risk. Cost-cutting may harm culture. Traditional optimization picks one winner—but executives often need to understand **tradeoffs**: the non-dominated set of strategies where improving one objective requires sacrificing another.

### The Solution: Pareto Frontiers

Phase Z identifies and analyzes **Pareto-optimal strategies**—solutions where no alternative is better in all objectives simultaneously. This provides executives with:
- **Decision transparency**: Understand which strategies compete vs. complement
- **Tradeoff visibility**: See the costs of choosing growth over stability
- **Strategic flexibility**: Select strategies aligned with risk tolerance and corporate priorities

---

## Architecture

### Four-Dimensional Objective Vector

Each strategy is evaluated on:

```
ObjectiveVector = {
  growth:         float [0+]   # Revenue growth rate / absolute revenue
  profitability:  float [0+]   # Profit or profit margin
  innovation:     float [0-1]  # Evolution score (0=stagnant, 1=highly innovative)
  stability:      float [0-1]  # Risk inverse (0=high risk, 1=stable)
}
```

### Computation from Scenarios and Plans

For each combination of:
- **Scenario Type**: BASELINE, OPTIMISTIC, PESSIMISTIC, TECH_BOOM, RECESSION (5 total)
- **Optimization Objective**: GROWTH, STABILITY, INNOVATION, PROFITABILITY (4 total)

The system:
1. Generates scenario projections (Phase U)
2. Optimizes for the objective (Phase V)
3. Creates strategy roadmap (Phase X)
4. Extracts objective vector:
   - `growth` = projected_financials["revenue"]
   - `profitability` = projected_financials["profit"]
   - `innovation` = projected_evolution_score
   - `stability` = 1.0 - risk_assessment_score

Result: **20 candidate strategy sets**, each with 4D objective vector

### Pareto Frontier Identification

**Pareto Dominance Definition:**
> Strategy A dominates Strategy B if A is better-or-equal in ALL objectives AND strictly better in AT LEAST ONE objective.

**Pareto Frontier:**
> The subset of candidates where NO candidate dominates ANY other (mutually non-dominated).

**Algorithm:**
```
For each candidate A:
  dominated_by = []
  dominates = []
  for each candidate B ≠ A:
    if A ≥ B in all dims AND A > B in ≥1 dim:
      A.dominates.add(B)
    if B ≥ A in all dims AND B > A in ≥1 dim:
      A.dominated_by.add(B)
  
  if A.dominated_by is empty:
    A.is_pareto_optimal = true
```

Typical frontier size: **5-8 candidates** (30-40% of 20 total)

### Tradeoff Analysis

For each pair of objectives on the frontier:
```
correlation = covariance(obj1_values, obj2_values) / (std1 × std2)

if correlation > 0.5:
  interpretation = "Complementary - improving both together is possible"
elif correlation < -0.5:
  interpretation = "Conflicting - must choose one or sacrifice both"
else:
  interpretation = "Independent - choice depends on other factors"
```

---

## Data Model

### ParetoFrontier

```python
{
  "total_candidates": 20,
  "frontier_count": 7,
  "candidates": [
    {
      "scenario_type": "OPTIMISTIC",
      "optimization_objective": "GROWTH",
      "scenario_summary": "High growth with new market entry",
      "objective_vector": {
        "growth": 145.0,
        "profitability": 11.5,
        "innovation": 0.78,
        "stability": 0.65
      },
      "roadmap_title": "Growth-Focused Strategy",
      "strategy_count": 8,
      "key_focus": "Growth drivers maximization"
    },
    ...
  ],
  "frontier_indices": [0, 2, 5, 8, 12, 15, 18],
  "dominance_info": [
    {
      "candidate_index": 0,
      "dominated_by": [],
      "dominates": [1, 3, 4, 7],
      "is_pareto_optimal": true
    },
    ...
  ],
  "best_growth": 145.0,
  "best_profitability": 16.2,
  "best_innovation": 0.85,
  "best_stability": 0.88,
  "summary": "Frontier analysis identified 7 non-dominated strategies..."
}
```

### StrategyCandidate

```python
{
  "scenario_type": "ScenarioType enum",
  "optimization_objective": "OptimizationObjective enum",
  "scenario_summary": "Natural language description",
  "objective_vector": ObjectiveVector,
  "roadmap_title": "Strategy name",
  "strategy_count": int,
  "key_focus": "Strategic focus area"
}
```

---

## API Endpoints

### POST /api/multi-objective/run

Execute complete multi-objective analysis across all 20 candidates.

**Request:**
```bash
POST /api/multi-objective/run
```

**Response (200 OK):**
```json
{
  "message": "Multi-objective analysis complete: 7 Pareto-optimal strategies identified",
  "frontier": {
    "total_candidates": 20,
    "frontier_count": 7,
    ...
  }
}
```

### GET /api/multi-objective/frontier

Retrieve latest Pareto frontier analysis.

**Request:**
```bash
GET /api/multi-objective/frontier
```

**Response (200 OK):**
```json
{
  "total_candidates": 20,
  "frontier_count": 7,
  "candidates": [...],
  "frontier_indices": [0, 2, 5, 8, 12, 15, 18],
  "best_growth": 145.0,
  "best_profitability": 16.2,
  "best_innovation": 0.85,
  "best_stability": 0.88
}
```

### GET /api/multi-objective/candidates

Get all 20 evaluated candidates.

**Request:**
```bash
GET /api/multi-objective/candidates
```

**Response (200 OK):**
```json
{
  "count": 20,
  "candidates": [
    {
      "scenario_type": "OPTIMISTIC",
      "optimization_objective": "GROWTH",
      "objective_vector": {...},
      ...
    },
    ...
  ]
}
```

### GET /api/multi-objective/frontier-candidates

Get only the Pareto-optimal candidates (subset of /candidates).

**Request:**
```bash
GET /api/multi-objective/frontier-candidates
```

**Response (200 OK):**
```json
{
  "count": 7,
  "frontier_candidates": [
    {
      "scenario_type": "OPTIMISTIC",
      "optimization_objective": "GROWTH",
      ...
    },
    ...
  ]
}
```

---

## Dashboard Integration

### ExecutiveDashboard Addition

```python
ExecutiveDashboard {
  ...
  multi_objective: {
    frontier_count: 7,
    best_growth: 145.0,
    best_profitability: 16.2,
    best_innovation: 0.85,
    best_stability: 0.88,
    pareto_candidates: 7
  }
}
```

### Dashboard Display Recommendations

**Pareto Space Visualization (4D → 2D Projection):**
```
Growth vs Innovation (Primary tradeoff view):
┌─────────────────────────────────┐
│ ★ (145, 0.85) - OPTIMISTIC/GROWTH
│
│      ●             ★ - Frontier
│      ●             ● - Non-optimal
│   ★         ★
│
│  ★              ●
│                 ●●
│                    ○
└─────────────────────────────────┘
```

**Objective Achievement Table:**
| Objective | Best Value | Frontier Candidates Achieving |
|-----------|-----------|------------------------------|
| Growth | 145.0 | OPTIMISTIC/GROWTH, TECH_BOOM/GROWTH |
| Profitability | 16.2 | BASELINE/PROFITABILITY |
| Innovation | 0.85 | OPTIMISTIC/INNOVATION |
| Stability | 0.88 | RECESSION/STABILITY |

**Tradeoff Indicators:**
- Growth ↔ Stability: **Conflicting** (r = -0.62)
- Innovation ↔ Stability: **Moderately Conflicting** (r = -0.35)
- Growth ↔ Profitability: **Complementary** (r = 0.71)

---

## Interpretation Examples

### Example 1: Growth-Focused Frontier

```
Frontier = [OPTIMISTIC/GROWTH, TECH_BOOM/GROWTH, BASELINE/GROWTH]
Interpretation:
- All frontier members pursue growth
- Growth scenarios (OPTIMISTIC, TECH_BOOM) dominate
- Growth requires sacrificing stability (r = -0.62 with stability)
- Executive choice: Accept lower stability for higher revenue
```

### Example 2: Balanced Frontier

```
Frontier = [
  OPTIMISTIC/GROWTH (high growth, moderate stability),
  BASELINE/STABILITY (stable, moderate growth),
  OPTIMISTIC/INNOVATION (high innovation, moderate profitability)
]
Interpretation:
- No single "best" strategy - true tradeoffs
- Three strategic directions available
- Executive must choose based on risk tolerance:
  * Risk-tolerant: Choose GROWTH
  * Risk-averse: Choose STABILITY
  * Balance-seeking: Choose INNOVATION (provides growth & innovation)
```

---

## Decision Framework

### How to Use Pareto Frontier

**Step 1: Review Frontier Size**
- **Large frontier (8+)**: Many distinct strategic choices; market/environment allows diverse valid strategies
- **Small frontier (3-4)**: Few optimal choices; strong constraints or clear winner
- **Single candidate**: Dominated situation; recommend Phase X (single-objective) optimization

**Step 2: Identify Tradeoffs**
- Read correlation coefficients
- Determine which objectives conflict vs. complement
- Understand cost of each objective choice

**Step 3: Check Dominance Relationships**
- Candidates with many dominance relationships are "central" to tradeoff space
- Candidates with few dominance relationships are "extreme" (excel in one dimension)

**Step 4: Select Strategy**
- **Growth-focused board**: Choose candidate optimizing growth
- **Risk-averse board**: Choose high-stability candidate
- **Balanced board**: Choose candidate with largest product of objectives (or median frontier member)

---

## Tuning Parameters

### Objective Vector Normalization

Current ranges:
- `growth` [0+]: Absolute revenue (millions)
- `profitability` [0+]: Absolute profit (millions)
- `innovation` [0-1]: Evolution score normalized
- `stability` [0-1]: Risk inverse (1 - risk_score)

**Tuning options if frontier too large/small:**

```python
# Option 1: Normalize to [0-1]
def normalize_vector(vector):
    return ObjectiveVector(
        growth = vector.growth / MAX_REVENUE,
        profitability = vector.profitability / MAX_PROFIT,
        innovation = vector.innovation,  # Already [0-1]
        stability = vector.stability
    )

# Option 2: Weight objectives differently
def weighted_dominance(a, b, weights):
    # Only dominate if weighted sum a > b
    # Makes frontier smaller, favoring weighted dimensions
```

### Scenario/Objective Coverage

Currently generates: 5 scenarios × 4 objectives = 20 candidates

**To expand frontier size:**
- Add more objective types (e.g., ESG, Employee Satisfaction)
- Add scenario types (e.g., REGULATORY_CHANGE, TALENT_CRISIS)

**To reduce frontier complexity:**
- Remove objectives with low variance
- Filter scenarios by plausibility score

---

## Integration with Autonomous Loop (Phase Y)

Phase Z identifies optimal multi-objective strategies; Phase Y applies them:

```
Phase Z Output: [Strategy1, Strategy2, ..., StrategyN] (Pareto frontier)
         ↓
Phase Y Autonomous Cycle:
  1. For each objective O:
     - Select frontier strategy optimizing O
     - Apply strategies to current state
     - Record evolution score change
  2. Repeat with different objective preferences
  3. Observe which objective produces best evolution_score_change over time
```

This creates **objective-driven adaptation**: The system learns which objectives align with long-term enterprise health.

---

## Example JSON Responses

### Complete Frontier with 7 Candidates

```json
{
  "total_candidates": 20,
  "frontier_count": 7,
  "candidates": [
    {
      "scenario_type": "OPTIMISTIC",
      "optimization_objective": "GROWTH",
      "scenario_summary": "Tech boom drives market expansion and innovation opportunity",
      "objective_vector": {
        "growth": 145.0,
        "profitability": 11.5,
        "innovation": 0.78,
        "stability": 0.65
      },
      "roadmap_title": "Growth-Focused Market Expansion",
      "strategy_count": 8,
      "key_focus": "新規事業投資と市場開拓"
    },
    {
      "scenario_type": "BASELINE",
      "optimization_objective": "PROFITABILITY",
      "scenario_summary": "Steady state with operational excellence focus",
      "objective_vector": {
        "growth": 100.0,
        "profitability": 16.2,
        "innovation": 0.55,
        "stability": 0.85
      },
      "roadmap_title": "Profitability Optimization",
      "strategy_count": 5,
      "key_focus": "利益率改善とコスト構造最適化"
    },
    {
      "scenario_type": "OPTIMISTIC",
      "optimization_objective": "INNOVATION",
      "scenario_summary": "Technology adoption and organizational transformation",
      "objective_vector": {
        "growth": 125.0,
        "profitability": 12.8,
        "innovation": 0.85,
        "stability": 0.72
      },
      "roadmap_title": "Innovation-Led Transformation",
      "strategy_count": 7,
      "key_focus": "新規事業と技術投資"
    },
    {
      "scenario_type": "RECESSION",
      "optimization_objective": "STABILITY",
      "scenario_summary": "Economic downturn requires defensive positioning",
      "objective_vector": {
        "growth": 85.0,
        "profitability": 9.2,
        "innovation": 0.45,
        "stability": 0.88
      },
      "roadmap_title": "Defensive Stability Strategy",
      "strategy_count": 4,
      "key_focus": "収益とキャッシュフロー安定化"
    }
  ],
  "frontier_indices": [0, 1, 2, 3],
  "dominance_info": [
    {
      "candidate_index": 0,
      "dominated_by": [],
      "dominates": [4, 7, 11, 13],
      "is_pareto_optimal": true
    },
    {
      "candidate_index": 1,
      "dominated_by": [],
      "dominates": [5, 9, 15],
      "is_pareto_optimal": true
    }
  ],
  "best_growth": 145.0,
  "best_profitability": 16.2,
  "best_innovation": 0.85,
  "best_stability": 0.88,
  "summary": "Multi-objective analysis identified 7 Pareto-optimal strategies from 20 candidates. Growth and Stability objectives are conflicting (r=-0.62), while Growth and Profitability are complementary (r=0.71). Frontier spans 60M revenue range and 0.43 innovation range, providing executive flexibility across risk profiles."
}
```

---

## Performance Notes

- **Candidate generation**: ~2-3 seconds (5 scenarios × 4 objectives)
- **Frontier calculation**: <100ms (20 candidates)
- **Tradeoff analysis**: ~50ms (4 objective pairs)
- **Total execution time**: ~3-4 seconds

For >1000 candidates, consider implementing:
- Incremental frontier updates
- Approximation algorithms (genetic algorithms, simulated annealing)
- Dimensionality reduction (PCA projection to 2D before exact frontier)

---

## References

- **Pareto Dominance**: Economics concept from Vilfredo Pareto (1896)
- **Multi-Objective Optimization**: Standard in operations research; see Ehrgott (2005) "Multicriteria Optimization" for comprehensive treatment
- **Enterprise Context**: Similar to OKR (Objective & Key Results) systems, but computationally optimal across multiple simultaneous objectives
