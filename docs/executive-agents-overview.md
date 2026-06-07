# Executive Agents（経営チームエージェント）概要

## 什么是 Executive Agents

Executive Agents は、経営チーム（CEO / CFO / CMO / CTO / CHRO / COO）を独立したAIエージェントとしてモデル化する機能です。各エージェントが自分の評価関数で戦略候補を評価し、議論・合意形成を通じて最終戦略を選択います。

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Executive Agents (経営チーム)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │   CEO   │  │   CFO   │  │   CMO   │  │   CTO   │  │   CHRO  │   │
│  │  Agent  │  │  Agent  │  │  Agent  │  │  Agent  │  │  Agent  │   │
│  ├─────────┤  ├─────────┤  ├─────────┤  ├─────────┤  ├─────────┤   │
│  │成長・全局│  │財務・ risk│  │市場・顧客│  │技術・革新│  │人材・組織│   │
│  │vote=1.5 │  │vote=1.2 │  │vote=1.0 │  │vote=1.0 │  │vote=1.0 │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
│       │            │            │            │            │        │
│       └────────────┴────────────┴────────────┴────────────┘        │
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                 Executive Council (経営会議)                    │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │  1. 各エージェントが全候補をスコアリング                         │  │
│  │  2. 投票生成 (AgentVote)                                       │  │
│  │  3. 重み付き集約 (weighted_average)                            │  │
│  │  4. 勝者選択 + 合意度計算                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│                    ExecutiveDecisionResult                          │
└─────────────────────────────────────────────────────────────────────┘
```

## エージェントロール

| ロール | 重点領域 | 投票重み | 主な関心事 |
|--------|----------|----------|------------|
| **CEO** | 全社戦略・成長・持続可能性 | 1.5 | 全社成長、競争優位、ステークホルダー価値 |
| **CFO** | 財務・投資・リスク管理 | 1.2 | 現金準備高、投資対効果、財務リスク、コスト管理 |
| **CMO** | 市場・顧客・ブランド | 1.0 | 市場シェア、顧客獲得、ブランド価値、マーケティングROI |
| **CTO** | 技術戦略・イノベーション | 1.0 | 技術革新、DX、技術負債、プラットフォーム |
| **CHRO** | 人材・組織・文化 | 1.0 | 人材確保、従業員エンゲージメント、組織文化、Diversity |
| **COO** | 執行・オペレーション | 1.1 | 業務執行、効率化、品質管理、サプライチェーン |

## スコアリングアルゴリズム

### 基本スコア計算

```python
base = (
    agent.growth_weight * vector.growth +
    agent.profitability_weight * vector.profitability +
    agent.innovation_weight * vector.innovation +
    agent.stability_weight * vector.stability
)
```

### エージェント固有補正

```python
# リスク補正：CFO はリスク回避
risk_penalty = agent.risk_aversion * candidate.risk_index * 0.2

# コスト補正：CFO はコスト敏感
cost_penalty = agent.cost_sensitivity * candidate.estimated_cost * 0.15

# 人材補正：CHRO は人材影響重視
people_bonus = agent.people_focus * candidate.people_impact_score * 0.1

# テクノロジー補正：CTO は技術影響重視
tech_bonus = agent.technology_focus * candidate.technology_impact_score * 0.1

# 市場補正：CMO は市場影響重視
market_bonus = agent.market_focus * candidate.market_impact_score * 0.1

final_score = base - risk_penalty - cost_penalty + people_bonus + tech_bonus + market_bonus
```

## 合意形成

### 重み付き平均

```python
def aggregate_votes(votes, role_weights):
    candidate_scores = {}
    
    for vote in votes:
        w = role_weights.get(vote.role, 1.0)
        weighted_score = vote.score * w
        candidate_scores[vote.candidate_id] += weighted_score
    
    selected_id = max(candidate_scores.items(), key=lambda x: x[1])[0]
    return selected_id
```

### デフォルト投票重み

```python
ROLE_WEIGHTS = {
    ExecutiveRole.CEO: 1.5,   # 最終決定権
    ExecutiveRole.CFO: 1.2,    # 財務チェック
    ExecutiveRole.CMO: 1.0,
    ExecutiveRole.CTO: 1.0,
    ExecutiveRole.CHRO: 1.0,
    ExecutiveRole.COO: 1.1,    # 執行チェック
}
```

### 合意度

```python
def calculate_consensus_level(votes, role_weights):
    max_votes / total_weight >= 0.8 → "high"
    max_votes / total_weight >= 0.5 → "medium"
    else → "low"
```

## API エンドポイント

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| GET | `/api/executives/agents` | エージェント一覧取得 |
| POST | `/api/executives/agents` | エージェント設定更新 |
| POST | `/api/executives/decide` | 経営会議実行 |
| GET | `/api/executives/council-summary` | 会議概要取得 |
| GET | `/api/executives/perspectives` | 各エージェントの視点 |
| GET | `/api/executives/markdown` | Markdown出力 |
| POST | `/api/executives/agents/reset` | デフォルトにリセット |

## 使用例

### 1. エージェント一覧取得

```bash
GET /api/executives/agents
```

```json
{
  "count": 6,
  "agents": [
    {
      "role": "CEO",
      "name": "CEO Agent",
      "focus_area": "全社戦略・成長・持続可能性",
      "vote_weight": 1.5,
      "weights": {
        "growth": 0.30,
        "profitability": 0.25,
        "innovation": 0.25,
        "stability": 0.20
      },
      "characteristics": {
        "risk_aversion": 0.4,
        "cost_sensitivity": 0.5,
        "people_focus": 0.6
      }
    },
    ...
  ]
}
```

### 2. 経営会議実行

```bash
POST /api/executives/decide
```

```json
{
  "message": "Executive decision completed",
  "decision": {
    "selected_candidate_id": "growth_max_growth",
    "aggregated_score": 0.823,
    "method": "weighted_average"
  },
  "summary": {
    "agent_count": 6,
    "candidate_count": 8,
    "selected_strategy": "growth_max_growth",
    "top_supporter": "CEO",
    "consensus_level": "medium"
  },
  "votes": [
    {"role": "CEO", "candidate_id": "growth_max_growth", "score": 0.85, ...},
    {"role": "CFO", "candidate_id": "profit_max_profit", "score": 0.78, ...},
    ...
  ],
  "perspectives": [
    {"role": "CEO", "focus": "全社戦略", "top_choice": "growth_max_growth", "score": 0.85},
    {"role": "CFO", "focus": "財務・リスク", "top_choice": "profit_max_profit", "score": 0.78},
    ...
  ]
}
```

### 3. 各エージェントの視点

```bash
GET /api/executives/perspectives
```

```json
{
  "perspectives": [
    {
      "role": "CEO",
      "focus": "全社戦略・成長・持続可能性",
      "top_choice": "growth_max_growth",
      "score": 0.85,
      "rationale": "base=0.75, risk_penalty=0.04, ..."
    },
    {
      "role": "CFO",
      "focus": "財務・投資・リスク管理",
      "top_choice": "profit_max_profit",
      "score": 0.78,
      "rationale": "base=0.68, risk_penalty=0.08, ..."
    }
  ]
}
```

## 自律ループとの統合

### 現在のフロー

```
Intent → Pareto Frontier → Intent-based Selection → 戦略選択
```

### 新しいフロー（Executive Agents）

```
Intent → Pareto Frontier → Executive Council Decision → 戦略選択
```

```python
# 自律エンタープライズサービスでの使用
def select_strategy_with_executive_council(frontier):
    decision = executive_agent_service.run_executive_decision(frontier)
    selected = find_candidate_by_id(frontier, decision.selected_candidate_id)
    return selected
```

## ダッシュボード統合

```python
class ExecutiveDecisionSummary(BaseModel):
    selected_candidate_id: str
    aggregated_score: float
    top_supporting_roles: List[str]
    consensus_level: str
```

## テスト

| テストファイル | 説明 |
|----------------|------|
| `test_executive_agent_engine.py` | Engine のユニットテスト |
| `test_executive_agent_service.py` | サービス層のテスト |
| `test_executive_agent_api.py` | API エンドポイントのテスト |

## 関連ドキュメント

- [Corporate Intent Overview](corporate-intent-overview.md)
- [Multi-Objective Optimization Overview](multi-objective-optimization-overview.md)
- [Autonomous Loop Overview](autonomous-loop-overview.md)