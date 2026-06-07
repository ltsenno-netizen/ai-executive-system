# Step AK: Multi-Company Comparative Intelligence

## Overview

**Multi-Company Comparative Intelligence** is a strategic layer that enables the AI executive system to understand and analyze its own identity, culture, consciousness evolution, and strategic positioning *in relation to peer companies*.

This layer transforms the system from a single-company introspection engine into a multi-dimensional comparative intelligence platform.

### Key Capability

> "How is our company different from competitors on dimensions of consciousness, culture, strategy, narrative, and meta-cognition?"

---

## Architecture

### Layer Stack

```
┌─────────────────────────────────────────────────────────────┐
│  REST API Layer (routes/multi_company_comparative.py)        │
│  - POST /api/companies/compare                               │
│  - GET /api/companies/compare/latest                         │
│  - GET /api/companies/compare/{report_id}                    │
│  - GET /api/companies/compare/{report_id}/markdown           │
│  - GET /api/companies                                        │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  Service Layer (services/multi_company_comparative_service.py)│
│  - compare_companies()                                        │
│  - get_last_comparison()                                      │
│  - get_report_by_id()                                         │
│  - generate_markdown_report()                                 │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  Engine Layer (services/multi_company_comparative_engine.py)  │
│  - compute_comparative_metrics()                              │
│  - cluster_companies()                                        │
│  - build_dimension_analyses()                                 │
│  - build_comparison_report()                                  │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  Model Layer (models/multi_company_comparative_model.py)      │
│  - CompanyProfile                                             │
│  - ComparativeMetric                                          │
│  - CompanyCluster                                             │
│  - MultiCompanyComparisonReport                               │
│  - MultiCompanyComparisonSummary (Dashboard)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Models

### CompanyProfile

Comprehensive profile of a single company for comparison.

```python
class CompanyProfile(BaseModel):
    company: CompanyId                           # Company identifier
    consciousness_clarity: float                 # How clear the company's identity (0-1)
    evolution_phase: str                         # Phase: REACTIVE, INTENTIONAL, EMERGENT
    evolution_speed: float                       # Rate of consciousness evolution (0-1)
    frontier_health: float                       # Strategic frontier health (0-1)
    frontier_score: float                        # Frontier analysis score (0-100)
    culture_profile: Dict[str, float]            # Culture dimensions
    risk_posture: float                          # Risk-seeking vs stable (0=stable, 1=aggressive)
    narrative_consistency: float                 # Theme consistency (0-1)
    narrative_clarity: float                     # Narrative coherence (0-1)
    meta_cognition_score: float                  # Self-awareness maturity (0-1)
    scenario_resilience: Dict[str, float]        # Resilience per scenario
    learning_agility: float                      # Capacity to learn/adapt (0-1)
```

### ComparativeMetric

Single metric computed across all companies.

```python
class ComparativeMetric(BaseModel):
    metric_id: str                      # Unique identifier
    name: str                           # Human-readable name
    category: str                       # consciousness, evolution, frontier, culture, narrative, meta_cognition, scenario
    description: str                    # What it measures
    values: Dict[str, float]            # company_id → value
    best_company_id: Optional[str]      # Company with highest value
    worst_company_id: Optional[str]     # Company with lowest value
    best_value: Optional[float]         # Highest value
    worst_value: Optional[float]        # Lowest value
    average_value: Optional[float]      # Average across all companies
```

### CompanyCluster

Classification of companies into archetypes.

```python
class CompanyCluster(BaseModel):
    cluster_id: str                     # System identifier
    cluster_name: str                   # AGGRESSIVE_INNOVATOR, STABLE_OPERATOR, etc.
    description: str                    # Cluster characteristics
    company_ids: List[str]              # Companies in this cluster
    defining_traits: Dict[str, float]   # Trait values that define this cluster
```

### MultiCompanyComparisonReport

Complete comparison output.

```python
class MultiCompanyComparisonReport(BaseModel):
    report_id: str                              # UUID
    companies: List[CompanyId]                  # Companies compared
    comparison_date: datetime
    metrics: List[ComparativeMetric]            # All comparative metrics
    clusters: List[CompanyCluster]              # Archetype classifications
    dimensions: List[ComparisonDimension]       # Dimension-level analysis
    narrative_summary: str                      # Executive narrative
    strategic_implications: List[str]           # Actionable insights
```

---

## Comparison Dimensions

The engine analyzes companies across **7 key dimensions**:

### 1. **Consciousness**
- **Metric**: `consciousness_clarity`
- **What**: How clearly does the company understand its own identity and purpose?
- **Range**: 0-1 (low clarity → high clarity)
- **Implication**: Low clarity = identity confusion, strategic drift; High clarity = strong vision

### 2. **Evolution**
- **Metrics**: `evolution_speed`, `evolution_phase`
- **What**: How fast is the company transitioning through consciousness phases?
- **Phases**: REACTIVE → INTENTIONAL → EMERGENT
- **Implication**: Fast evolution = adaptability; Slow = stability/inertia

### 3. **Frontier** (Strategic Positioning)
- **Metrics**: `frontier_health`, `frontier_score`
- **What**: Health of strategic exploration and innovation frontier
- **Range**: 0-1 and 0-100
- **Implication**: Strong frontier = expansion capacity; Weak = consolidation mode

### 4. **Culture**
- **Metric**: `risk_posture` + culture dimensions (innovation, execution, risk_aversion, etc.)
- **What**: Risk tolerance, organizational values, behavioral norms
- **Range**: 0=stable/conservative, 1=aggressive/risk-seeking
- **Implication**: Affects strategy viability, decision speed, talent attraction

### 5. **Narrative**
- **Metrics**: `narrative_consistency`, `narrative_clarity`
- **What**: How consistent and coherent is the company's public/internal story?
- **Range**: 0-1
- **Implication**: Strong narrative = aligned stakeholders, powerful brand; Weak = confusion, internal misalignment

### 6. **Meta-Cognition** (Self-Awareness)
- **Metrics**: `meta_cognition_score`, `learning_agility`
- **What**: Does the company understand its own blindspots, patterns, strengths/weaknesses?
- **Range**: 0-1
- **Implication**: High self-awareness = capacity to improve; Low = unaware of vulnerabilities

### 7. **Scenario Resilience**
- **Metrics**: `scenario_resilience` per scenario type
- **What**: How resilient is the company to different market scenarios?
- **Scenarios**: BASELINE, RECESSION, TECH_BOOM, OPTIMISTIC, PESSIMISTIC
- **Range**: 0-1
- **Implication**: Identifies scenario blindspots, needed hedging strategies

---

## Company Archetypes (Clusters)

The engine classifies companies into **5 archetypal clusters**:

### 1. **Aggressive Innovator**
- **Traits**: High risk_posture (>0.65), strong frontier_health (>0.6), high learning_agility (>0.6)
- **Behavior**: Rapid experimentation, market expansion, high strategic risk
- **Competitive Threat**: High
- **Strategic Positioning**: Frontier explorer

### 2. **Stable Operator**
- **Traits**: Low risk_posture (<0.4), moderate frontier_health (<0.65), high narrative_consistency (>0.7)
- **Behavior**: Steady operations, incremental improvement, strong consistency
- **Competitive Threat**: Low
- **Strategic Positioning**: Operational excellence

### 3. **Transformational**
- **Traits**: High evolution_speed (>0.65), high consciousness_clarity (>0.65), balanced risk (0.35-0.65)
- **Behavior**: Undergoing major strategic/cultural change, identity evolution
- **Competitive Threat**: Medium (unpredictable trajectory)
- **Strategic Positioning**: In transition

### 4. **Awakening**
- **Traits**: High meta_cognition_score (>0.7), high learning_agility (>0.65), improving consciousness_clarity (>0.55)
- **Behavior**: Self-aware, learning-driven, improving capabilities
- **Competitive Threat**: Emerging
- **Strategic Positioning**: Capability building

### 5. **Struggling**
- **Traits**: Low across most metrics
- **Behavior**: Limited adaptation, clarity issues, capability gaps
- **Competitive Threat**: Low (may be acquisition target or market failure)
- **Strategic Positioning**: Distressed

---

## REST API

### 1. List Available Companies
```http
GET /api/companies

Response:
{
  "companies": [
    {"company_id": "self", "name": "Our Company"},
    {"company_id": "competitor_a", "name": "Competitor A"}
  ],
  "count": 2
}
```

### 2. Generate Comparison
```http
POST /api/companies/compare

Request Body:
[
  {"company_id": "self", "name": "Our Company"},
  {"company_id": "competitor_a", "name": "Competitor A"},
  {"company_id": "competitor_b", "name": "Competitor B"}
]

Response: MultiCompanyComparisonReport
```

### 3. Get Latest Comparison
```http
GET /api/companies/compare/latest

Response: MultiCompanyComparisonReport
```

### 4. Get Specific Report
```http
GET /api/companies/compare/{report_id}

Response: MultiCompanyComparisonReport
```

### 5. Export as Markdown
```http
GET /api/companies/compare/{report_id}/markdown

Response:
{
  "report_id": "uuid",
  "format": "markdown",
  "content": "# Multi-Company Comparative Intelligence Report\n..."
}
```

### 6. Dashboard Summary
```http
GET /api/companies/compare/latest/summary

Response: MultiCompanyComparisonSummary
{
  "companies": ["Our Company", "Competitor A"],
  "strongest_company": "competitor_a",
  "weakest_company": "self",
  "cluster_count": 2,
  "cluster_labels": {...},
  "key_insight": "...",
  "last_compared": "2026-05-12T..."
}
```

---

## Dashboard Integration

The comparison summary is automatically integrated into the Executive Dashboard:

```python
dashboard.multi_company_comparison_summary: Optional[MultiCompanyComparisonSummary]
```

**Fields**:
- `companies`: List of company names
- `strongest_company`: Company ID with highest overall score
- `weakest_company`: Company ID with lowest overall score
- `cluster_count`: Number of archetypes identified
- `cluster_labels`: Mapping of archetype name → [company_ids]
- `key_insight`: Single most important finding
- `last_compared`: Timestamp of comparison

---

## Usage Examples

### Example 1: Self vs. Competitors
```python
from src.backend.app.models.multi_company_comparative_model import CompanyId
from src.backend.app.services.multi_company_comparative_service import MultiCompanyComparativeService

service = MultiCompanyComparativeService()

companies = [
    CompanyId(company_id="self", name="Our Tech Startup"),
    CompanyId(company_id="google", name="Google"),
    CompanyId(company_id="microsoft", name="Microsoft"),
    CompanyId(company_id="apple", name="Apple"),
]

report = service.compare_companies(companies)

# Analyze narrative consistency
narrative_metrics = [m for m in report.metrics if m.metric_id == "narrative_consistency"]
for m in narrative_metrics:
    print(f"{m.name}: Best={m.best_company_id} ({m.best_value:.2f}), "
          f"Worst={m.worst_company_id} ({m.worst_value:.2f})")

# See cluster assignments
for cluster in report.clusters:
    print(f"{cluster.cluster_name}: {', '.join(cluster.company_ids)}")
```

### Example 2: Business Unit Comparison
```python
# Compare business units within same company as separate "company_ids"
companies = [
    CompanyId(company_id="bu_cloud", name="Cloud Services"),
    CompanyId(company_id="bu_enterprise", name="Enterprise Solutions"),
    CompanyId(company_id="bu_ai", name="AI Research"),
]

report = service.compare_companies(companies)

# Understand which BU is most risk-seeking, most self-aware, etc.
print(report.narrative_summary)
print(report.strategic_implications)
```

### Example 3: Scenario Resilience Analysis
```python
report = service.compare_companies(companies)

# Extract scenario resilience metrics
scenario_metrics = [m for m in report.metrics if m.category == "scenario"]

for metric in scenario_metrics:
    print(f"{metric.name}:")
    for company_id, value in metric.values.items():
        print(f"  {company_id}: {value:.2f}")
```

---

## Strategic Implications Generated

The engine automatically identifies:

1. **Gap Analysis**: Quantified differences between companies on each metric
2. **Heterogeneity**: Diversity of strategies and profiles across competitors
3. **Evolution Dynamics**: Which companies are evolving fastest
4. **Self-Awareness Gap**: Vulnerability of companies with low meta-cognition
5. **Clustering Insights**: Which companies play similar strategies

---

## Test Coverage

- `test_multi_company_comparative_engine.py`: Metric computation, clustering, dimension analysis
- `test_multi_company_comparative_service.py`: Service layer, persistence, retrieval
- `test_multi_company_comparative_api.py`: All 6 REST endpoints, error handling
- `test_dashboard_multi_company_comparison.py`: Dashboard integration

---

## Data Persistence

Comparison reports are stored as JSON in:
```
data/multi_company_comparisons/{report_id}.json
```

Each report can be retrieved by ID or accessed as the "latest" comparison.

---

## Roadmap Extensions

1. **Real-time Intelligence**: Integrate with market data APIs for live competitor tracking
2. **Predictive Modeling**: ML model to predict competitor moves based on historical patterns
3. **Supply Chain Mapping**: Understand competitive advantage through supply chain analysis
4. **Talent Analytics**: Compare talent acquisition, retention, skill profiles
5. **Patent/IP Analysis**: Track innovation intensity through IP filings
6. **Sentiment Analysis**: Monitor brand perception and narrative sentiment over time
7. **Scenario Stress Testing**: Model how each competitor responds to future scenarios

---

## Conceptual Bridge

**Before (Single-Company):**
> "Who are we? What's our culture? How are we evolving?"

**After (Multi-Company Comparative):**
> "Who are we *relative to our competitors*? Where do we have advantage? Where are we vulnerable? What can we learn from peers?"

This transforms the system into a **competitive intelligence engine** that sees the company not in isolation, but in a competitive ecosystem.
