# Corporate Story Overview

## Overview

The Corporate Story Model (Step W: Corporate Narrative Integration) represents the culmination of the AI Executive System. It synthesizes all accumulated intelligence—past company history, current state, future scenarios, and self-optimization recommendations—into a coherent, compelling corporate narrative.

The system answers the fundamental question: **"What is our company's journey, and where are we heading?"**

## Purpose

The Corporate Story enables enterprises to:

1. **Understand Their History**: Contextualize past events and transitions
2. **Assess Current State**: Evaluate present organizational capabilities
3. **Explore Future Possibilities**: Compare multiple scenario outcomes
4. **Define Optimization Direction**: Articulate recommended strategic shifts
5. **Tell a Unified Story**: Communicate compelling narrative to stakeholders

## Architecture

### Core Components

#### Corporate Story Model (src/backend/app/models/corporate_story_model.py)
- **CorporateStorySection**: Individual chapter with title and narrative content
- **CorporateStory**: Complete multi-chapter story with summary

#### Corporate Story Engine (src/backend/app/services/corporate_story_engine.py)
- `build_history_section()`: Past narrative construction
- `build_current_state_section()`: Present state articulation
- `build_scenario_section()`: Future possibilities description
- `build_optimization_section()`: Recommended transformations
- `build_integrated_narrative_section()`: Unified strategic narrative
- `generate_corporate_story()`: Comprehensive story generation

#### Corporate Story Service (src/backend/app/services/corporate_story_service.py)
- Story generation and persistence
- Result retrieval and aggregation
- Markdown and JSON storage in `/data/stories/`

#### API Routes (src/backend/app/routes/corporate_story.py)
- POST /api/story/generate/{period}
- GET /api/story/{period}
- GET /api/story/

#### Dashboard Integration
- **CorporateStorySummary**: Condensed story display
- Integrated into ExecutiveDashboard
- Period and summary visible in dashboard

## Story Structure

The generated story consists of five chapters:

### 1. 企業の歩み（Company History）
**Content**: Past leadership transitions, cultural evolution, environmental shocks, evolution score trajectory

**Purpose**: Establishes organizational foundation and adaptive capacity

**Example Narrative**:
```
この企業は複数のリーダーシップ転換を経験しており、各段階で異なる経営スタイルと戦略的方向性が展開されてきました。
企業文化は革新性を中心として進化し、組織の価値観と行動様式に深い影響を与えてきました。
進化スコアは 0.65 に達しており、企業が環境変化に適応し、継続的に進化していることを示しています。
```

### 2. 現在の姿（Current State）
**Content**: Present culture dimensions, PEST factors, executive team composition, evolution status

**Purpose**: Establishes baseline for future comparison

**Example Narrative**:
```
現在の企業文化は、革新性と安定性のバランスを保ち、進化スコア 0.65 という水準にあります。
経営チームは CEO, CFO, CMO で構成され、多様な専門性と視点を持つメンバーが統括しています。
外部環境は経済 0.50、技術 0.60、社会 0.50 の状況にあり、複数の機会と課題が存在します。
```

### 3. 未来の可能性（Scenario Futures）
**Content**: Multiple scenario outcomes with evolution scores and financial projections

**Purpose**: Presents strategic options and trade-offs

**Example Narrative**:
```
ベースラインシナリオでは、現在の傾向が継続し、進化スコア 0.50、推定売上 110.0 に到達する可能性があります。

楽観シナリオでは、好況環境と技術革新が企業成長を加速させ、進化スコア 0.75、推定売上 130.0 に到達する可能性があります。

不況シナリオでは、コスト構造と効率性が経営の鍵となります。進化スコア 0.45、推定売上 85.0 に留まる可能性があります。
```

### 4. 最適化の方向性（Self-Optimization）
**Content**: Recommended objective, strategies, culture shifts, leadership adjustments

**Purpose**: Articulates transformation pathway

**Example Narrative**:
```
### 目的：GROWTH
選択されたシナリオ：optimistic

### 推奨戦略
1. 新規事業投資を強化 (優先度: 1, 効果予測: 80%)
2. マーケティング予算を増大 (優先度: 2, 効果予測: 60%)

### 文化シフト
- innovation_culture: +0.10
  理由: 好況期には革新性を高める
- aggressiveness_culture: +0.05
  理由: 市場機会への対応力強化
```

### 5. 企業の未来への道（Integrated Narrative）
**Content**: Synthesis of history, present strengths, scenario selection rationale, unified vision

**Purpose**: Provides coherent strategic direction

**Example Narrative**:
```
企業は複数の環境変化とリーダーシップ交代を乗り越えてきました。これらの経験から、組織の適応力と継続性の重要性を学んできています。

進化スコア 0.65 が示すように、企業は継続的な改善と学習を実現しています。多様な経営陣と柔軟な組織文化が、変化への対応力を高めています。

複数シナリオの分析結果、GROWTH を最大化する方向が最有望です。選択されたシナリオは 'optimistic' であり、期待される進化スコアは 0.75 に達します。

企業は自ら進化し続ける『学習する組織』として、過去の成果と現在の強みを活かしながら、未来のチャレンジに主体的に対応していきます。
```

## Usage

### Generate Story
```
POST /api/story/generate/2026-04
```

Response:
```json
{
  "message": "Generated corporate story for period: 2026-04",
  "story": {
    "period": "2026-04",
    "sections": [
      {
        "title": "企業の歩み",
        "content": "..."
      },
      {
        "title": "現在の姿",
        "content": "..."
      },
      {
        "title": "未来の可能性",
        "content": "..."
      },
      {
        "title": "最適化の方向性",
        "content": "..."
      },
      {
        "title": "企業の未来への道",
        "content": "..."
      }
    ],
    "summary": "企業は過去の経験を踏まえ、現在の強みを活かしながら、未来に向けて GROWTH を目指す方向へ進化しています。期待される進化スコアは 0.75 です。"
  }
}
```

### Retrieve Story
```
GET /api/story/2026-04
```

### Get Latest Story
```
GET /api/story/
```

## Data Persistence

Stories are stored in `/data/stories/`:
- `story_2026-04.json`: Story in JSON format
- `story_2026-04.md`: Story in Markdown format

## Dashboard Display

The dashboard shows:
```
Corporate Story Summary
Period: 2026-04
Summary: 企業は過去の経験を踏まえ、現在の強みを活かしながら、
未来に向けて GROWTH を目指す方向へ進化しています。
期待される進化スコアは 0.75 です。
```

## Generation Logic

The story generation synthesizes:

1. **Company History Service**: Past events, CEO transitions, culture trends
2. **Culture Service**: Current culture dimensions
3. **Environment Service**: Current PEST analysis
4. **Scenario Service**: Future scenario projections
5. **Self-Optimization Service**: Recommended transformation plan
6. **Evolution Service**: Current evolution metrics

## Testing

Comprehensive test coverage:
- `test_corporate_story_engine.py`: Engine logic validation
- `test_corporate_story_service.py`: Service operations
- `test_corporate_story_api.py`: API endpoint validation
- `test_dashboard_corporate_story_summary.py`: Dashboard integration

## Future Extensions

Potential enhancements:
- Multi-language narrative generation
- Executive summary with key metrics
- Stakeholder-specific narratives (investor, employee, customer)
- Historical narrative comparison and trend analysis
- AI-powered narrative generation with LLM enhancement
- Interactive narrative exploration interface
- Narrative export (PDF, presentation formats)
