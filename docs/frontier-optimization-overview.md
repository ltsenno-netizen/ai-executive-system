# Frontier Optimization Overview (Step AD)

## Vision
**戦略空間そのものを最適化し、企業が選べる戦略の質を向上させる**

"Optimize the strategy space itself to improve the quality of strategies available for selection"

Step AD enhances the AI Executive System by moving beyond candidate evaluation (Steps AA-AC) to **meta-optimization**: improving the Pareto frontier itself. Rather than just selecting the best strategy from available options, we analyze and optimize the frontier to ensure executives have access to truly excellent choices.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│            Frontier Optimization Service (AD)               │
│                   Orchestration Layer                       │
└─────────────────────────────────────────────────────────────┘
        ↓              ↓              ↓
    Analysis       Gradient      Optimization
    Engine        Engine        Engine
    ↓              ↓              ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Shape    │  │Tradeoff  │  │ Strategy │
│Analysis  │  │Gradient  │  │ Space    │
└──────────┘  └──────────┘  └──────────┘
```

### Three-Layer Frontier Analysis

#### 1. **Frontier Shape Analysis** (frontend_analysis_engine.py)
Analyzes the geometric properties and structure of the Pareto frontier.

**Key Metrics:**
- **Convexity Analysis**: Measure how "curved" the frontier is
  - Convexity Ratio: 0-1 scale (0=concave, 1=convex)
  - Non-convex Regions: Identification of areas with poor tradeoffs
  
- **Extreme Points**: Identify strategies with maximum/minimum in each objective
  - One per dimension (Growth, Profitability, Innovation, Stability)
  - Guide frontier shape understanding
  
- **Tradeoff Cliffs**: Identify regions with steep tradeoffs
  - High gradient regions where small changes have large impacts
  - Critical decision points for executives
  
- **Frontier Density**: Measure crowding and distribution
  - Overall Density: Percentage of objective space covered
  - Clustering Coefficient: How grouped strategies are
  - Sparse vs. Dense Regions: Local distribution analysis
  
- **Objective Correlation**: Pearson correlation between pairs
  - Identify which objectives naturally align or conflict
  - Guide understanding of fundamental tradeoffs

**Usage:**
```python
from app.services.frontier_analysis_engine import FrontierAnalysisEngine
from app.models.multi_objective_model import ParetoFrontier

engine = FrontierAnalysisEngine()
shape_report = engine.analyze_frontier_shape(frontier)

print(f"Convexity: {shape_report.convexity_analysis.convexity_ratio}")
print(f"Clustering: {shape_report.frontier_density.clustering_coefficient}")
print(f"Correlations: {shape_report.objective_correlations}")
```

#### 2. **Tradeoff Gradient Analysis** (tradeoff_gradient.py)
Estimates rates of change between objectives along the frontier.

**Key Metrics:**
- **Local Gradients**: dTarget/dSource at each point
  - Computed using nearest-neighbor analysis
  - Represents sacrifice required for gains
  
- **Tradeoff Profiles**: Comprehensive profile for each objective pair
  - Average Gradient: Central tendency
  - Min/Max Gradient: Extreme points
  - Gradient Stability: Consistency across frontier
  
- **Dominant Tradeoff**: Most significant objective pair
  - Highest average magnitude
  - Most critical strategic decision axis
  
- **Neutral Pairs**: Objectives with low correlation
  - Opportunities for simultaneous gains
  - Key enablers for multi-objective success
  
- **Frontier Quality Score**: Overall quality assessment
  - Tradeoff Diversity: Coverage of different tradeoff types
  - Gradient Stability: Consistency of tradeoffs
  - Gradient Balance: Symmetry across objective pairs
  - Objective Independence: Ability to optimize independently

**Usage:**
```python
from app.services.tradeoff_gradient import TradeoffGradientEngine

engine = TradeoffGradientEngine()
gradient_report = engine.compute_tradeoff_gradients(frontier)

print(f"Dominant Tradeoff: {gradient_report.dominant_tradeoff}")
print(f"Quality Score: {gradient_report.quality_scores}")
for insight in gradient_report.actionable_insights:
    print(f"- {insight}")
```

#### 3. **Strategy Space Optimizer** (strategy_space_optimizer.py)
Identifies optimization opportunities and improves frontier characteristics.

**Key Capabilities:**
- **Redundant Cluster Detection**
  - Distance-based clustering (threshold: 5.0)
  - Identifies similar strategies with minimal differentiation
  - Calculates cluster similarity metric (0-1)
  
- **Strategy Gap Identification**
  - Three gap types:
    1. Growth-Stability Imbalance: Lack of balanced strategies
    2. Innovation-Stability Gap: Missing innovation + stability combinations
    3. Sparse Regions: Underutilized areas of objective space
  
- **New Candidate Generation** (Integration point)
  - Gap location and severity analysis
  - Suggested scenario/objective to explore
  - Placeholder for new candidate creation
  
- **Optimized Frontier Generation**
  - Removes redundant clusters
  - Adds candidates for identified gaps
  - Improved frontier with better distribution
  
- **Frontier Potential Estimation**
  - Reconstruction Quality: How well optimized frontier preserves original
  - Density Improvement: Better distribution
  - Gap Filling Potential: Closure of identified gaps
  - Estimated Improvement: Overall potential gain

**Usage:**
```python
from app.services.strategy_space_optimizer import StrategySpaceOptimizer
from app.models.corporate_intent_model import CorporateIntent

optimizer = StrategySpaceOptimizer()
intent = intent_service.get_intent()
optimization_report = optimizer.optimize_strategy_space(frontier, intent)

print(f"Redundant Clusters: {len(optimization_report.redundant_clusters)}")
print(f"Strategy Gaps: {len(optimization_report.strategy_gaps)}")
print(f"Improvement Potential: {optimization_report.frontier_potential}")
```

### Orchestration Service

**FrontierOptimizationService** coordinates all three engines in a complete cycle.

**9-Step Optimization Cycle:**
```
1. Get Current Frontier
   └─→ Retrieve latest Pareto frontier from MultiObjectiveService
   
2. Analyze Frontier Shape
   └─→ Run FrontierAnalysisEngine (convexity, density, extremes, cliffs)
   
3. Compute Tradeoff Gradients
   └─→ Run TradeoffGradientEngine (gradients, profiles, quality)
   
4. Identify Optimization Opportunities
   └─→ Run StrategySpaceOptimizer (clusters, gaps, improvements)
   
5. Estimate Frontier Potential
   └─→ Calculate improvement metrics and recommendations
   
6. Generate Optimized Frontier
   └─→ Create improved candidate set
   
7. Build Recommendations
   └─→ Synthesize insights for Intent + Agents
   
8. Save Results
   └─→ Persist to JSON files for history tracking
   
9. Return Complete Result
   └─→ Shape + Gradient + Opportunity + Potential + Insights
```

**Health Scoring:**
```python
health_score = (
    convexity_ratio * 0.3 +
    (1 - clustering_coefficient) * 0.2 +
    gradient_stability * 0.25 +
    (1 - gap_count/max_gaps) * 0.25
)

Status: 
  ≥ 0.75 → "healthy" (green)
  ≥ 0.5  → "warning" (yellow)
  ≥ 0.25 → "critical" (red)
  < 0.25 → "unknown"
```

## Integration Points

### With Corporate Intent (Step AA)
- Intent weights guide frontier shape interpretation
- Recommendations weighted by Intent priorities
- Learning from frontier optimization feeds back to Intent

### With Executive Agents (Step AB)
- Agent preferences influence gap identification
- Agent voting patterns inform tradeoff interpretation
- Recommendations align with agent consensus

### With Autonomous Loop (Step AC)
- Frontier health triggers optimization decisions
- Optimized frontier becomes basis for next cycle
- Executive decisions inform which optimizations matter most

## REST API

### POST /api/frontier/optimize
Execute a complete optimization cycle.

**Response:**
```json
{
  "frontier_id": "frontier_2026_q1",
  "period": "2026-01",
  "frontier_size": 12,
  "shape": {
    "convexity_ratio": 0.82,
    "extreme_points": 4,
    "clustering_coefficient": 0.65
  },
  "gradients": {
    "dominant_tradeoff": "growth vs profitability",
    "magnitude": 0.73,
    "quality_score": 0.71
  },
  "opportunities": {
    "redundant_clusters": 2,
    "strategy_gaps": 3,
    "gap_severity_average": 0.58
  },
  "potential": {
    "estimated_improvement": 0.28,
    "reconstruction_quality": 0.94,
    "gap_filling_potential": 0.62
  },
  "insights": ["Frontier has good convexity...", "Dominant tradeoff between..."],
  "recommendations": ["Remove 2 redundant strategies...", "Explore innovation-stability gap..."]
}
```

### GET /api/frontier/analysis
Get detailed shape analysis.

**Response includes:**
- Complete convexity analysis with non-convex regions
- All extreme points identified
- Tradeoff cliffs with steep gradients
- Density metrics and clustering
- Objective correlations

### GET /api/frontier/gradients
Get gradient analysis.

**Response includes:**
- Key gradients (top 5 by magnitude)
- Dominant tradeoff with interpretation
- Neutral objective pairs
- Quality scores for all metrics
- Actionable insights for each key gradient

### GET /api/frontier/optimized
Get optimization recommendations.

**Response includes:**
- Redundant clusters for removal
- Strategy gaps with severity and location
- New candidate suggestions
- Recommended actions
- Improvement estimate

### GET /api/frontier/health
Get frontier health score.

**Response:**
```json
{
  "score": 0.78,
  "status": "healthy",
  "issues": ["slight clustering in middle region"],
  "last_optimization": "2026-01-15T10:30:00Z"
}
```

### GET /api/frontier/history
Get optimization history.

**Query Parameters:**
- `limit`: Number of historical records (default: 10)

### GET /api/frontier/summary
Get complete frontier state summary.

**Response includes:**
- Frontier state (size, status)
- Characteristics (convexity, density, correlations)
- Readiness assessment
- Health score
- Improvement potential
- Top recommendations

## Key Concepts

### Pareto Frontier Quality Dimensions

| Dimension | Metric | Interpretation |
|-----------|--------|-----------------|
| **Shape** | Convexity Ratio | How "smooth" the tradeoff curve is |
| **Structure** | Clustering | Whether strategies are distributed or grouped |
| **Gradients** | Tradeoff Magnitude | How much sacrifice is required |
| **Coverage** | Frontier Density | How much objective space is covered |
| **Correlations** | Objective Relationships | Which objectives naturally align |
| **Gaps** | Sparse Regions | Where good strategies are missing |
| **Health** | Overall Score | Composite readiness for decision-making |

### Decision-Making Implications

**High Convexity + Smooth Gradients:**
- Strong tradeoffs are clear and consistent
- Easy for executives to understand sacrifices
- Frontier is "well-formed" for strategic thinking

**Low Density + Clustering:**
- Options are concentrated in specific areas
- Other objective combinations poorly explored
- Optimization needed for balanced portfolio

**High Gradient Stability:**
- Tradeoffs are consistent across frontier
- No "weird" regions with unexpected behaviors
- Predictable strategic implications

**Neutral Objective Pairs:**
- Potential for simultaneous gains
- Strategic enablers worth pursuing
- May indicate missing strategies that improve both

## Example Workflow

### 1. Analyze Current Frontier
```python
service = FrontierOptimizationService()
cycle_result = service.run_frontier_optimization_cycle()
```

### 2. Understand Frontier Quality
```python
health = service.get_frontier_health_score()
if health["score"] < 0.6:
    print("Frontier optimization recommended")
```

### 3. Explore Shape Characteristics
```python
shape = cycle_result.shape_analysis
print(f"Convexity: {shape['convexity_analysis']['convexity_ratio']}")
print(f"Clustering: {shape['frontier_density']['clustering_coefficient']}")
```

### 4. Review Tradeoff Insights
```python
gradients = cycle_result.gradient_analysis
print(f"Dominant Tradeoff: {gradients['dominant_tradeoff']}")
for insight in gradients['actionable_insights']:
    print(f"- {insight}")
```

### 5. Identify Optimization Opportunities
```python
opps = cycle_result.optimization_opportunities
for gap in opps['strategy_gaps']:
    print(f"Gap: {gap['location']} (severity: {gap['severity']})")
    print(f"  Rationale: {gap['rationale']}")
```

### 6. Review Recommendations
```python
for rec in cycle_result.recommendations['actions']:
    print(f"- {rec}")
```

### 7. Dashboard Integration
The frontier health and recommendations automatically appear on the executive dashboard:
```
Frontier Optimization Insights
├─ Health Score: 0.78 (Healthy)
├─ Top Issues: [clustering in region X]
├─ Recommendations:
│  ├─ Remove redundant cluster with s4, s5
│  ├─ Explore innovation-stability gap
│  └─ Improve distribution in profitability range
└─ Last Optimization: 2026-01-15
```

## Testing

Comprehensive test suites validate all components:

- **test_frontier_analysis_engine.py**: Shape analysis, convexity, density
- **test_tradeoff_gradient.py**: Gradient computation, quality scoring
- **test_strategy_space_optimizer.py**: Gap/cluster identification, recommendations
- **test_frontier_optimization_service.py**: Service orchestration, health scoring

Run tests:
```bash
pytest tests/test_frontier_analysis_engine.py -v
pytest tests/test_tradeoff_gradient.py -v
pytest tests/test_strategy_space_optimizer.py -v
pytest tests/test_frontier_optimization_service.py -v
```

## Performance Considerations

### Computational Complexity
- Shape Analysis: O(n²) for pairwise distances
- Gradient Computation: O(n × k) where k = nearest neighbors
- Gap Identification: O(n² × m) where m = objective dimensions
- Overall: O(n²) for typical frontier sizes (n < 100)

### Optimization Guidelines
- Frontier Size: Works efficiently with 10-100 candidates
- Objective Dimensions: Designed for 4 primary objectives
- Run Frequency: Recommended weekly or monthly
- Historical Tracking: Keeps last 10-20 optimization runs

## Future Enhancements

1. **Automated Gap Filling**: Generate and evaluate new candidates
2. **Multi-Period Optimization**: Track frontier evolution
3. **Agent-Specific Filtering**: Tailor recommendations to agent preferences
4. **Scenario Integration**: Link frontier optimization to scenario planning
5. **Real-time Monitoring**: Continuous frontier health tracking
6. **Predictive Analysis**: Forecast frontier evolution

## References

- [Multi-Objective Model](multi-objective-optimization-overview.md)
- [Corporate Intent](autonomous-loop-integration-overview.md)
- [Executive Agents](executive-agents-overview.md)
- [Autonomous Loop](autonomous-loop-integration-overview.md)
