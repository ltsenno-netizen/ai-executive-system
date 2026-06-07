# Narrative Intelligence Overview (Step AG)

## Executive Summary

**Narrative Intelligence** is an advanced system that automatically generates contextually appropriate narratives for different audiences by integrating consciousness, evolution, intent, agents, frontier, and autonomous loop data. The system determines "how the organization should speak" based on its current state, ensuring consistent, authentic, and strategically aligned communication across all stakeholder groups.

**Key Achievement**: 企業が今どのように語るべきかを自動判断し、文脈別の語り（IR Narrative, Internal Culture Narrative, Brand Narrative, Public Narrative, Alliance Narrative, Crisis/Transformation/Growth Narratives）を生成するシステム

---

## I. Narrative Intelligence Architecture

### Core Components

```
Narrative Intelligence System
├── Models (narrative_intelligence_model.py)
│   ├── NarrativeAudience (8 audiences)
│   ├── NarrativeStyle (6 styles)
│   ├── NarrativeContext (integrated system data)
│   ├── GeneratedNarrative (output with metadata)
│   ├── NarrativeIntelligenceMetrics
│   └── NarrativeIntelligenceReport
│
├── Engine (narrative_intelligence_engine.py)
│   ├── build_narrative_context() - System integration
│   ├── _select_style() - Audience-style mapping
│   ├── generate_narrative() - Core generation
│   └── _compose_narrative_text() - Content composition
│
├── Service (narrative_intelligence_service.py)
│   ├── generate_narrative() - Public API
│   ├── get_narrative_history() - Retrieval
│   ├── export_narrative_markdown() - Export
│   ├── get_narrative_metrics() - Analytics
│   └── generate_narrative_report() - Reporting
│
├── API Routes (narrative_intelligence.py)
│   ├── POST /api/narrative/generate/{audience}
│   ├── GET /api/narrative/{id}
│   ├── GET /api/narrative/history
│   ├── GET /api/narrative/{id}/markdown
│   ├── GET /api/narrative/audiences
│   ├── GET /api/narrative/styles
│   ├── GET /api/narrative/metrics
│   └── GET /api/narrative/report
│
└── Dashboard Integration
    └── NarrativeIntelligenceSummary in ExecutiveDashboard
```

### System Integration Points

**Step AE (Corporate Consciousness)**: Identity, purpose, direction, risk posture, coherence score
**Step AF (Consciousness Evolution)**: Current phase (EMERGING → MATURING), momentum, stability
**Step AA (Corporate Intent)**: Mission, vision, values, strategic direction
**Step AB (Executive Agents)**: Latest decisions, confidence scores, strategic alignment
**Step AD (Frontier Optimization)**: Health score, optimization status
**Step AC (Autonomous Loop)**: Current cycle status, performance metrics

---

## II. Audience × Style Matrix

### Narrative Audiences

| Audience | Primary Style | Communication Focus | Key Stakeholders |
|----------|---------------|-------------------|------------------|
| **INVESTORS** | ANALYTICAL | Financial performance, strategic value, risk management | Shareholders, analysts, financial institutions |
| **EMPLOYEES** | INSPIRATIONAL | Culture, purpose, growth opportunities, team spirit | Internal workforce, management, HR |
| **CUSTOMERS** | CONFIDENT | Product/service value, reliability, innovation, partnership | Current/potential customers, partners |
| **PUBLIC** | FORMAL | Corporate citizenship, community impact, transparency | Media, regulators, general public |
| **PARTNERS** | TRANSPARENT | Collaboration, mutual benefit, strategic alignment | Business partners, suppliers, alliances |
| **CRISIS** | TRANSPARENT | Situation assessment, action plan, stakeholder support | All stakeholders during crises |
| **TRANSFORMATION** | CONFIDENT | Change vision, progress updates, future state | Stakeholders during major changes |
| **GROWTH** | INSPIRATIONAL | Opportunity focus, momentum, shared success | Stakeholders during expansion phases |

### Narrative Styles

| Style | Tone Characteristics | Use Cases |
|-------|---------------------|-----------|
| **FORMAL** | Professional, structured, objective | Public communications, regulatory filings |
| **INSPIRATIONAL** | Motivational, visionary, aspirational | Employee communications, growth narratives |
| **ANALYTICAL** | Data-driven, logical, evidence-based | Investor relations, performance reports |
| **TRANSPARENT** | Open, honest, accountable | Crisis communications, partnership discussions |
| **CONFIDENT** | Assured, self-assured, decisive | Customer communications, transformation updates |
| **HUMBLE** | Modest, grounded, appreciative | Community relations, post-crisis recovery |

---

## III. Context Integration Logic

### Narrative Context Building

```python
def build_narrative_context(audience: NarrativeAudience) -> NarrativeContext:
    return NarrativeContext(
        audience=audience,
        style=select_style(audience),  # Audience → Style mapping
        phase=evolution_state.current_phase,  # From Step AF
        intent=corporate_intent,  # From Step AA
        decision=latest_executive_decision,  # From Step AB
        frontier_health=frontier.health_score,  # From Step AD
        culture_profile=current_culture,  # Culture service
        environment_state=current_environment  # Environment service
    )
```

### Phase-Based Framing

| Phase | Narrative Framing | Example Opening |
|-------|------------------|----------------|
| **EMERGING** | Exploration, foundation-building | "We are in the early stages of our journey..." |
| **GROWING** | Learning, capability expansion | "We are experiencing significant growth..." |
| **CONSOLIDATING** | Stabilization, systematization | "We are consolidating our gains..." |
| **TRANSFORMING** | Innovation, paradigm shifts | "We are undergoing transformation..." |
| **MATURING** | Wisdom, strategic maturity | "We have reached maturity..." |

### Frontier Health Interpretation

| Health Score | Interpretation | Narrative Element |
|-------------|----------------|------------------|
| 0.8-1.0 | Strong optimization | "Our frontier is enabling exploration of new possibilities" |
| 0.6-0.8 | Good progress | "We are actively working on frontier optimization" |
| 0.4-0.6 | Needs improvement | "We are addressing frontier challenges" |
| 0.0-0.4 | Critical issues | "We are committed to strengthening our frontier capabilities" |

---

## IV. Narrative Generation Process

### 1. Context Aggregation
- **Consciousness Phase**: Determines maturity framing and risk posture
- **Corporate Intent**: Provides mission/vision/values alignment
- **Executive Decisions**: Incorporates latest strategic actions
- **Frontier Health**: Indicates optimization and innovation capacity
- **Culture Profile**: Reflects organizational dynamics and momentum
- **Environment State**: Considers external context and pressures

### 2. Content Composition

```python
def compose_narrative_text(context: NarrativeContext) -> str:
    # 1. Phase-based framing
    # 2. Intent alignment section
    # 3. Executive decision rationale
    # 4. Frontier health interpretation
    # 5. Culture & environment reflection
    # 6. Audience-specific conclusion
    return final_narrative
```

### 3. Key Message Extraction

**Automatic extraction based on:**
- Sentence structure analysis
- Action word detection (commit, focus, build, create, deliver)
- Length filtering (20-100 characters)
- Top 5 messages prioritized

### 4. Tone Marker Detection

**Detected markers:**
- **Confident**: committed, strong, capable, determined
- **Inspirational**: inspire, vision, purpose, together, embrace
- **Analytical**: data, analysis, metrics, optimize, strategic
- **Transparent**: open, transparent, accountable, address, proactive
- **Formal**: formal, professional, structured, systematic

---

## V. API Usage Examples

### Generate Narrative for Investors

```bash
curl -X POST "http://localhost:8000/api/narrative/generate/INVESTORS" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
    "narrative_id": "narr_1234567890abcdef",
    "audience": "INVESTORS",
    "style": "ANALYTICAL",
    "text": "We are consolidating our gains, refining our operations, and building sustainable excellence. Our core intent drives us forward: To create sustainable value through innovation. Recent executive decisions reflect our strategic direction: Approved $50M investment in green technology. Our optimization frontier is strong, enabling us to explore new possibilities and maximize value creation. Our culture is dynamic and evolving, supporting our ability to adapt and innovate. We remain committed to delivering sustainable value and long-term growth for our stakeholders.",
    "key_messages": [
        "Approved $50M investment in green technology",
        "Our optimization frontier is strong",
        "We remain committed to delivering sustainable value"
    ],
    "tone_markers": ["confident", "analytical", "committed"],
    "timestamp": "2024-01-15T14:30:00Z"
}
```

### Get Narrative History

```bash
curl -X GET "http://localhost:8000/api/narrative/history?limit=10"
```

**Response:**
```json
[
    {
        "narrative_id": "narr_1234567890abcdef",
        "audience": "INVESTORS",
        "style": "ANALYTICAL",
        "text": "We are consolidating our gains...",
        "key_messages": ["Approved $50M investment...", "Our optimization frontier is strong"],
        "tone_markers": ["confident", "analytical"],
        "timestamp": "2024-01-15T14:30:00Z"
    }
]
```

### Export as Markdown

```bash
curl -X GET "http://localhost:8000/api/narrative/narr_1234567890abcdef/markdown"
```

**Response:**
```markdown
# Narrative for INVESTORS

**Generated:** 2024-01-15 14:30:00 UTC
**Style:** ANALYTICAL

## Narrative Text

We are consolidating our gains, refining our operations, and building sustainable excellence...

## Key Messages

- Approved $50M investment in green technology
- Our optimization frontier is strong
- We remain committed to delivering sustainable value

## Tone Markers

confident, analytical, committed

---
*Generated by Narrative Intelligence System*
```

### Get Available Audiences

```bash
curl -X GET "http://localhost:8000/api/narrative/audiences"
```

**Response:**
```json
[
    {
        "audience": "INVESTORS",
        "description": "Financial stakeholders and investment community"
    },
    {
        "audience": "EMPLOYEES",
        "description": "Internal workforce and organizational members"
    }
]
```

### Generate Comprehensive Report

```bash
curl -X GET "http://localhost:8000/api/narrative/report?period=quarterly"
```

**Response:**
```json
{
    "period": "quarterly",
    "generated_at": "2024-01-15T14:30:00Z",
    "metrics": {
        "total_narratives": 24,
        "audience_distribution": {
            "INVESTORS": 6,
            "EMPLOYEES": 8,
            "CUSTOMERS": 4,
            "PUBLIC": 3,
            "PARTNERS": 3
        },
        "style_distribution": {
            "ANALYTICAL": 6,
            "INSPIRATIONAL": 8,
            "CONFIDENT": 4,
            "FORMAL": 3,
            "TRANSPARENT": 3
        },
        "last_generated": "2024-01-15T14:30:00Z"
    },
    "recent_narratives": [...],
    "audience_effectiveness": {
        "INVESTORS": {
            "count": 6,
            "avg_key_messages": 2.3
        }
    },
    "recommendations": [
        "Increase narrative generation for PUBLIC audience",
        "Balance style distribution across audiences"
    ]
}
```

---

## VI. Dashboard Integration

### Executive Dashboard Display

The Narrative Intelligence section appears in the executive dashboard with:

```json
{
    "narrative_intelligence": {
        "latest_narratives": {
            "INVESTORS": "We are consolidating our gains, refining our operations...",
            "EMPLOYEES": "Together, we are building an organization that inspires...",
            "CUSTOMERS": "We are committed to delivering exceptional value..."
        },
        "recent_audiences": ["INVESTORS", "EMPLOYEES", "CUSTOMERS"],
        "total_narratives": 24,
        "last_generation": "2024-01-15T14:30:00Z",
        "key_messages": [
            "Approved $50M investment in green technology",
            "Our optimization frontier is strong",
            "Culture supports innovation and adaptation"
        ],
        "tone_markers": ["confident", "inspirational", "analytical"],
        "frontier_reflection": 0.85,
        "intent_alignment": 0.92
    }
}
```

### Dashboard Visualization Elements

1. **Latest Narratives Panel**
   - Audience-specific narrative previews (200 chars + "...")
   - Click-through to full narrative
   - Generation timestamp

2. **Key Messages Summary**
   - Top messages from recent narratives
   - Categorized by audience
   - Trend indicators

3. **Tone Markers Display**
   - Current dominant tones
   - Tone distribution chart
   - Consistency indicators

4. **Metrics Overview**
   - Total narratives generated
   - Audience distribution
   - Generation frequency

5. **Integration Health**
   - Frontier reflection score
   - Intent alignment score
   - System integration status

---

## VII. Sample Generated Narratives

### Investor Narrative (ANALYTICAL Style)

**Context**: CONSOLIDATING phase, high frontier health, recent investment decision

"We are consolidating our gains, refining our operations, and building sustainable excellence. Our core intent drives us forward: To create sustainable value through innovation. Our vision is clear: Leading the industry in sustainable technology. Recent executive decisions reflect our strategic direction: Approved $50M investment in green technology. Our optimization frontier is strong, enabling us to explore new possibilities and maximize value creation. Our culture is dynamic and evolving, supporting our ability to adapt and innovate. We remain committed to delivering sustainable value and long-term growth for our stakeholders. Our data-driven approach ensures sustainable progress."

**Key Messages:**
- Approved $50M investment in green technology
- Our optimization frontier is strong
- We remain committed to delivering sustainable value

**Tone Markers:** confident, analytical, committed

### Employee Narrative (INSPIRATIONAL Style)

**Context**: GROWING phase, strong culture momentum, team-focused intent

"We are experiencing significant growth, expanding our capabilities and strengthening our position. Our core intent drives us forward: To create sustainable value through innovation. We are guided by our values: Innovation, Integrity, Excellence. Recent executive decisions reflect our strategic direction: Approved $50M investment in green technology. We are actively working on frontier optimization, balancing current performance with future potential. Our culture is dynamic and evolving, supporting our ability to adapt and innovate. Together, we will continue to build an organization that inspires, challenges, and rewards excellence. Let's embrace the future with confidence and purpose."

**Key Messages:**
- Together, we will continue to build an organization
- Our culture is dynamic and evolving
- We are guided by our values

**Tone Markers:** inspirational, confident, committed

### Crisis Narrative (TRANSPARENT Style)

**Context**: CRISIS audience triggered, low frontier health, high environment severity

"We are taking decisive action to address current challenges and emerge stronger. Our core intent drives us forward: To create sustainable value through innovation. Recent executive decisions reflect our strategic direction: Approved $50M investment in green technology. We are committed to strengthening our frontier capabilities to ensure long-term competitiveness. The external environment presents significant challenges that we are addressing proactively. We are taking decisive action to address current challenges and emerge stronger."

**Key Messages:**
- We are taking decisive action to address current challenges
- The external environment presents significant challenges
- We are committed to strengthening our frontier capabilities

**Tone Markers:** transparent, committed, proactive

---

## VIII. Performance & Analytics

### Metrics Tracked

- **Total Narratives**: Cumulative count of generated narratives
- **Audience Distribution**: Narrative count by audience type
- **Style Distribution**: Usage frequency of different styles
- **Generation Frequency**: Average narratives per day/week
- **Key Message Quality**: Average key messages per narrative
- **Tone Consistency**: Tone marker distribution and stability

### Effectiveness Measures

- **Audience Coverage**: Percentage of audiences with recent narratives
- **Content Freshness**: Average age of narratives by audience
- **Integration Health**: System component data availability
- **Generation Success Rate**: Percentage of successful generations

### Recommendations Engine

**Automatic recommendations based on:**
- Missing audience coverage
- Style distribution imbalance
- Generation frequency gaps
- Integration health issues
- Content freshness metrics

---

## IX. Configuration & Customization

### Style Mapping Customization

```python
# In narrative_intelligence_engine.py
def _select_style(audience: NarrativeAudience) -> NarrativeStyle:
    custom_mapping = {
        NarrativeAudience.INVESTORS: NarrativeStyle.ANALYTICAL,
        NarrativeAudience.EMPLOYEES: NarrativeStyle.INSPIRATIONAL,
        # Add custom mappings
        NarrativeAudience.CUSTOMERS: NarrativeStyle.CONFIDENT,
    }
    return custom_mapping.get(audience, NarrativeStyle.FORMAL)
```

### Content Templates

**Phase-specific templates:**
```python
PHASE_TEMPLATES = {
    ConsciousnessPhase.EMERGING: "We are in the early stages of our journey, discovering our path and building our foundation.",
    ConsciousnessPhase.GROWING: "We are experiencing significant growth, expanding our capabilities and strengthening our position.",
    # Custom templates
}
```

### Integration Weights

**Adjust component influence:**
```python
COMPONENT_WEIGHTS = {
    'phase': 0.3,      # 30% phase influence
    'intent': 0.25,    # 25% intent influence
    'decision': 0.2,   # 20% decision influence
    'frontier': 0.15,  # 15% frontier influence
    'culture': 0.1,    # 10% culture influence
}
```

### Persistence Configuration

```python
# In narrative_intelligence_service.py
NARRATIVES_DIR = Path("data/narratives")
MAX_HISTORY_RETAINED = 1000  # Maximum narratives to keep
AUTO_CLEANUP_DAYS = 365     # Auto-cleanup older narratives
```

---

## X. Integration Architecture

### System Dependencies

**Required Services:**
- Corporate Consciousness Evolution Service (Step AF)
- Corporate Intent Service (Step AA)
- Executive Agent Service (Step AB)
- Frontier Optimization Service (Step AD)
- Culture Service
- External Environment Service (Step AC)

**Graceful Degradation:**
- If any service unavailable → fallback to basic narrative
- Partial data → generate with available context
- Complete failure → return None (dashboard handles gracefully)

### Data Flow

```
System Components → Context Builder → Narrative Engine → Service Layer → API Routes → Dashboard
     ↓              ↓              ↓              ↓              ↓              ↓
   AE/AF/AA/AB/AD/AC → NarrativeContext → GeneratedNarrative → Persistence → REST API → UI Display
```

### Error Handling

**Service Level:**
- Component unavailability → fallback narratives
- Data validation errors → graceful degradation
- Persistence failures → in-memory operation

**API Level:**
- Invalid requests → 422 validation errors
- Service failures → 500 internal errors
- Not found → 404 errors

**Dashboard Level:**
- Service unavailable → null field (no display)
- Partial data → show available information
- Complete failure → section hidden

---

## XI. Testing Strategy

### Test Coverage

**test_narrative_context_builder.py**
- Context building with all system components
- Style selection logic
- Validation and error handling

**test_narrative_generation_engine.py**
- Narrative composition logic
- Key message extraction
- Tone marker detection
- Audience-specific content

**test_narrative_intelligence_service.py**
- Service lifecycle management
- Persistence operations
- Error handling and fallbacks

**test_narrative_intelligence_api.py**
- REST API endpoint testing
- Parameter validation
- Error response handling

**test_dashboard_narrative_intelligence.py**
- Dashboard integration
- Data aggregation
- Error handling in dashboard context

### Test Data Strategy

**Mock Services:** Comprehensive mocking of all dependent services
**Edge Cases:** Service failures, partial data, invalid inputs
**Integration Tests:** End-to-end narrative generation workflows
**Performance Tests:** Generation speed and memory usage

---

## XII. Troubleshooting

### Common Issues

**Narratives Not Generating**
- **Symptom**: API returns 500 error
- **Cause**: Dependent services unavailable
- **Solution**: Check service health, use fallback narratives

**Inconsistent Tone**
- **Symptom**: Tone markers don't match expected style
- **Cause**: Style mapping or content composition issues
- **Solution**: Review style selection logic and templates

**Missing Key Messages**
- **Symptom**: Empty key_messages array
- **Cause**: Content analysis algorithm issues
- **Solution**: Adjust message extraction patterns

**Dashboard Not Showing Narratives**
- **Symptom**: narrative_intelligence field is null
- **Cause**: Service integration failure
- **Solution**: Check service imports and initialization

### Performance Optimization

**Generation Speed:**
- Cache frequently accessed system data
- Optimize content analysis algorithms
- Use async processing for heavy computations

**Memory Usage:**
- Limit narrative history retention
- Implement cleanup policies
- Use streaming for large exports

**API Response Time:**
- Implement response caching
- Optimize database queries
- Use pagination for large result sets

---

## XIII. Future Enhancements

### Advanced Features

**Multi-language Support:**
- Narrative generation in multiple languages
- Cultural adaptation for global audiences
- Translation service integration

**Dynamic Style Learning:**
- ML-based style optimization
- Audience feedback integration
- A/B testing for narrative effectiveness

**Real-time Adaptation:**
- Event-driven narrative updates
- Social media sentiment analysis
- Real-time context monitoring

**Advanced Analytics:**
- Narrative impact measurement
- Stakeholder sentiment analysis
- Communication effectiveness metrics

### Integration Extensions

**External Systems:**
- Social media publishing
- Content management systems
- Marketing automation platforms

**Advanced AI:**
- GPT integration for enhanced generation
- Sentiment analysis for tone optimization
- Predictive analytics for narrative timing

---

## XIV. Success Metrics

### Quantitative Metrics

- **Generation Success Rate**: >95% successful generations
- **API Response Time**: <500ms average
- **Audience Coverage**: 100% audiences with recent narratives
- **Content Freshness**: <7 days average narrative age

### Qualitative Metrics

- **Stakeholder Feedback**: Positive reception scores
- **Communication Consistency**: Unified voice across channels
- **Strategic Alignment**: Narratives reflect organizational intent
- **Crisis Response Time**: <1 hour crisis narrative generation

### Business Impact

- **Stakeholder Trust**: Improved perception metrics
- **Crisis Management**: Faster, more effective responses
- **Brand Consistency**: Unified messaging across touchpoints
- **Strategic Communication**: Better alignment with business objectives

---

**Last Updated**: January 2024
**Status**: Production Ready
**Maintained By**: AI Executive System Team