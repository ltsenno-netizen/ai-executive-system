# Strategy Proposal Engine (Step X) Overview

## Overview

The Strategy Proposal Engine (Step X: 戦略提案エンジン) transforms scenario analysis, self-optimization plans, and corporate narratives into concrete, actionable strategic roadmaps. It answers the critical executive question: **"What specific strategies should we execute, and in what priority and timeline?"**

The engine synthesizes all upstream intelligence to generate:
- **Strategic Focus**: Primary business objective and direction
- **Prioritized Actions**: Specific initiatives ranked by priority and impact
- **Execution Timeline**: Short, mid, and long-term phasing
- **Risk Assessment**: Realistic appraisal of execution risks
- **Dependencies**: Prerequisites and sequencing logic

## Purpose

The Strategy Proposal Engine enables enterprises to:

1. **Translate Analysis into Action**: Convert optimization recommendations into executable strategies
2. **Establish Priorities**: Rank initiatives by business impact and feasibility
3. **Plan Execution**: Define realistic timelines (short/mid/long-term)
4. **Assess Risks**: Identify execution challenges and constraints
5. **Create Accountability**: Link strategies to measurable outcomes
6. **Communicate Direction**: Provide clear strategic narrative to organization

## Architecture

### Core Components

#### Strategy Model (src/backend/app/models/strategy_model.py)

**StrategyHorizon Enum**:
```python
class StrategyHorizon(str, Enum):
    SHORT_TERM = "short_term"   # 0-12 months: Quick wins, operational adjustments
    MID_TERM = "mid_term"       # 1-3 years: Business model changes, capability building
    LONG_TERM = "long_term"     # 3+ years: Cultural transformation, structural change
```

**StrategyRiskLevel Enum**:
```python
class StrategyRiskLevel(str, Enum):
    LOW = "low"          # Well-understood, proven execution path
    MEDIUM = "medium"    # Some uncertainty, manageable risk
    HIGH = "high"        # Significant uncertainty or organizational impact
```

**StrategyItem**: Individual strategic action
```python
class StrategyItem(BaseModel):
    title: str                           # "新規事業投資" など
    description: str                     # 詳細な説明
    horizon: StrategyHorizon            # 実行時間帯
    priority: int                        # 優先度 1-10
    expected_impact: float               # 期待される影響 0.0-1.0
    risk_level: StrategyRiskLevel       # リスクレベル
    dependencies: List[str]              # 前提条件 ("文化シフト完了後" など)
```

**StrategyRoadmap**: Complete execution plan
```python
class StrategyRoadmap(BaseModel):
    objective: OptimizationObjective     # 最適化目標 (GROWTH, STABILITY, etc.)
    selected_scenario: ScenarioType      # 選択したシナリオ
    key_focus: str                       # "成長ドライバーの最大化" など
    strategies: List[StrategyItem]       # 優先順位順に並んだ戦略リスト
    notes: Optional[str]                 # 背景や前提
```

#### Strategy Engine (src/backend/app/services/strategy_engine.py)

**Key Functions**:

1. **determine_key_focus(plan)**
   - Maps OptimizationObjective to strategic focus statement
   - Examples:
     - GROWTH → "成長ドライバーの最大化と新規市場開拓"
     - STABILITY → "収益とキャッシュフローの安定化"
     - INNOVATION → "新規事業・技術投資と組織革新"
     - PROFITABILITY → "利益率改善とコスト構造の最適化"

2. **build_strategy_items(plan, story)**
   - Converts SelfOptimizationPlan recommendations into StrategyItems
   - Assigns execution horizons:
     - SHORT_TERM: Cost, efficiency, organizational adjustments
     - MID_TERM: New business, investments, capability development
     - LONG_TERM: Cultural transformation, structural change
   - Estimates risk levels combining impact and uncertainty
   - Builds dependency chains (e.g., "culture shift must precede new business launch")

3. **build_strategy_roadmap(plan, story)**
   - Orchestrates complete roadmap generation
   - Sorts strategies by priority and expected impact
   - Includes corporate narrative context
   - Returns prioritized, sequenced action plan

#### Strategy Service (src/backend/app/services/strategy_service.py)

**Key Methods**:

- `generate_strategy_roadmap(objective)`: Generates and persists roadmap for objective
- `get_latest_strategy_roadmap(objective)`: Retrieves roadmap by objective or most recent
- `get_all_strategy_roadmaps()`: Retrieves all generated roadmaps

**Storage**: JSON files in `/data/strategy/{objective}.json`

#### API Routes (src/backend/app/routes/strategy.py)

- `POST /api/strategy/generate/{objective}`: Generate roadmap for objective
- `GET /api/strategy/latest`: Get most recent roadmap
- `GET /api/strategy/latest/{objective}`: Get latest roadmap for objective
- `GET /api/strategy/all`: Get all available roadmaps

#### Dashboard Integration

**Models** (executive_dashboard_model.py):
```python
class StrategyDashboardItem(BaseModel):
    title: str
    horizon: StrategyHorizon
    priority: int
    risk_level: StrategyRiskLevel

class StrategyDashboardSummary(BaseModel):
    objective: str
    selected_scenario: str
    key_focus: str
    top_strategies: List[StrategyDashboardItem]  # Top 5 strategies
```

**Integration** (executive_dashboard_service.py):
```python
def aggregate_strategy_summary() -> Optional[StrategyDashboardSummary]:
    # Gets latest roadmap and formats for dashboard display
    # Shows: objective, scenario, focus, top 5 priorities with horizons and risks
```

## Strategy Generation Logic

### 1. Focus Determination
Maps the optimization objective to a clear strategic focus:

| Objective | Focus | Key Actions |
|-----------|-------|------------|
| GROWTH | 成長ドライバーの最大化 | New markets, revenue expansion, M&A |
| STABILITY | 収益とCF安定化 | Reduce volatility, strengthen reserves |
| INNOVATION | 新規事業・技術投資 | R&D increase, new ventures, partnerships |
| PROFITABILITY | 利益率改善 | Cost reduction, pricing optimization |

### 2. Strategy Item Assignment
For each recommended strategy from the optimization plan:

**Horizon Logic**:
- Keywords like "新規", "投資", "協業" → MID_TERM
- Keywords like "文化", "構造", "変革" → LONG_TERM  
- Keywords like "コスト", "効率", "調整" → SHORT_TERM
- High impact (≥0.7) → MID_TERM default
- Lower impact → SHORT_TERM default

**Risk Estimation**:
```
risk_score = (expected_impact * 0.6) + (uncertainty * 0.4)
HIGH risk: score ≥ 0.7
MEDIUM risk: score 0.4-0.7
LOW risk: score < 0.4
```

**Dependencies**:
- New business strategies → depend on culture shift completion
- Cost reduction → depends on organizational adjustment
- Structural changes → depend on alignment and readiness

### 3. Roadmap Prioritization
Strategies sorted by:
1. Priority level (1-10, lower number = higher priority)
2. Expected impact (higher impact first as tiebreaker)

## JSON Structure Example

```json
{
  "objective": "GROWTH",
  "selected_scenario": "OPTIMISTIC",
  "key_focus": "成長ドライバーの最大化と新規市場開拓",
  "strategies": [
    {
      "title": "新規事業投資",
      "description": "テック企業との協業で新規事業化、期待売上増加30%",
      "horizon": "mid_term",
      "priority": 1,
      "expected_impact": 0.8,
      "risk_level": "medium",
      "dependencies": ["文化シフト: innovation_culture"]
    },
    {
      "title": "マーケティング予算増大",
      "description": "ブランド認知度向上と顧客開拓",
      "horizon": "short_term",
      "priority": 2,
      "expected_impact": 0.6,
      "risk_level": "low",
      "dependencies": []
    },
    {
      "title": "文化シフト: innovation_culture",
      "description": "イノベーション文化を+0.10向上させ、新規事業への組織準備",
      "horizon": "long_term",
      "priority": 3,
      "expected_impact": 0.6,
      "risk_level": "medium",
      "dependencies": []
    }
  ],
  "notes": "企業は過去のリーダーシップ交代と文化進化を踏まえ、現在の強みを活かしながら、OPTIMISTIC シナリオの実現を目指します。"
}
```

## Dashboard Display

The dashboard shows the strategy summary:

```
STRATEGY ROADMAP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objective: GROWTH
Scenario: OPTIMISTIC
Key Focus: 成長ドライバーの最大化と新規市場開拓

TOP 5 PRIORITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 新規事業投資
   Timeline: Mid-term (1-3 years)
   Priority: 1 | Risk: Medium | Impact: 0.8

2. マーケティング予算増大
   Timeline: Short-term (0-12 months)
   Priority: 2 | Risk: Low | Impact: 0.6

3. 文化シフト: innovation_culture
   Timeline: Long-term (3+ years)
   Priority: 3 | Risk: Medium | Impact: 0.6
```

## API Usage Examples

### Generate Strategy
```bash
POST /api/strategy/generate/GROWTH

Response:
{
  "message": "Generated strategy roadmap for objective: GROWTH",
  "roadmap": {
    "objective": "GROWTH",
    "selected_scenario": "OPTIMISTIC",
    "key_focus": "成長ドライバーの最大化と新規市場開拓",
    "strategies": [...]
  }
}
```

### Get Latest by Objective
```bash
GET /api/strategy/latest/STABILITY

Response:
{
  "objective": "STABILITY",
  "selected_scenario": "BASELINE",
  "key_focus": "収益とキャッシュフローの安定化",
  "strategies": [...]
}
```

### Get All Roadmaps
```bash
GET /api/strategy/all

Response:
{
  "roadmaps": [
    { "objective": "GROWTH", ... },
    { "objective": "STABILITY", ... },
    { "objective": "INNOVATION", ... }
  ]
}
```

## Execution Framework

### Short-term (0-12 months)
- Operational efficiency improvements
- Quick cost reductions
- Team capability enhancements
- Market positioning adjustments
- Target: 20-40% implementation of total roadmap

### Mid-term (1-3 years)
- New business launches
- Market expansion
- Capability building
- Strategic partnerships
- Target: 40-60% implementation of total roadmap

### Long-term (3+ years)
- Cultural transformation
- Structural reorganization
- Business model innovation
- Strategic repositioning
- Target: Final 20-40% implementation of total roadmap

## Risk Management

**Low-Risk Strategies** (execute first):
- Proven execution path
- Manageable dependencies
- Clear success metrics

**Medium-Risk Strategies** (execute with planning):
- Some execution uncertainty
- Dependent on other strategies
- Requires resource commitment

**High-Risk Strategies** (execute with caution):
- Significant organizational change
- External market uncertainty
- Requires strong leadership and change management

## Data Flow Integration

```
Scenario Results
    ↓
Self-Optimization Plan (with recommendations)
    ↓
Corporate Story (narrative context)
    ↓
[Strategy Engine]
    ↓
Strategy Roadmap (concrete action plan)
    ↓
Executive Dashboard (executive visibility)
```

## Testing

Comprehensive test coverage:
- `test_strategy_engine.py`: Engine logic validation (focus determination, item generation, roadmap building)
- `test_strategy_service.py`: Service operations (generation, retrieval, persistence)
- `test_strategy_api.py`: API endpoint validation
- `test_dashboard_strategy_summary.py`: Dashboard integration

## Key Metrics

Each strategy item captures:
- **Priority** (1-10): Relative importance to achieving objective
- **Expected Impact** (0.0-1.0): Potential contribution to objective
- **Risk Level** (LOW/MEDIUM/HIGH): Execution complexity/uncertainty
- **Timeline** (SHORT/MID/LONG): Realistic execution window

## Future Enhancements

- Scenario sensitivity analysis: How strategies change across scenarios
- Executive accountability: Track strategy execution against roadmap
- Outcome measurement: Link actual results to predicted impact
- Dynamic adjustment: Update roadmap based on actual execution progress
- Resource planning: Map strategies to required capabilities and budget
- Stakeholder communication: Generate strategy narratives for different audiences
- Strategy portfolio analysis: Balance across innovation, growth, stability
- Early warning system: Flag risk factors that could derail strategies

## Conclusion

The Strategy Proposal Engine brings strategic rigor and executable clarity to enterprise decision-making. By transforming scenario analysis and self-optimization recommendations into concrete, prioritized, time-sequenced strategies, it enables executives to move confidently from insight to action.

The roadmap provides both strategic direction and tactical clarity:
- **For the Board**: Clear understanding of strategic priorities and risks
- **For Executives**: Specific initiatives to drive organizational performance
- **For the Organization**: Transparent priorities and sequencing for execution
- **For Stakeholders**: Confidence in coherent, data-driven strategic direction
