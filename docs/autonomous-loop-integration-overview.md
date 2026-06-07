# Step AC: Autonomous Loop Integration（自律ループ統合）

## 概要

Step AC は、**Step AA (Corporate Intent)** と **Step AB (Executive Agents)** を **自律ループ** に統合し、企業が「議論しながら」自律進化するメカニズムを実装します。

これにより、システムは以下のサイクルを繰り返すようになります：

```
Intent → Multi-Objective Frontier → Executive Council Decision 
→ Strategy Selection → Execution → State Update → Intent Learning
```

## アーキテクチャ

### 従来のフロー（Step Y）

```
Intent 
  ↓
Pareto Frontier (戦略候補生成)
  ↓
Intent-based Selection (Intent に基づき選択)
  ↓
Strategy → Apply → Update
```

### Step AC: 新しいフロー

```
Intent (企業の意思)
  ↓
Pareto Frontier (戦略候補生成)
  ↓
Executive Agents Council Decision (経営チームが投票・合意形成)
  ↓
Selected Strategy → Apply → Update
  ↓
Intent Learning from Decisions & Results (投票傾向と結果から学習)
```

```
┌─────────────────────────────────────────────────────────────────┐
│            Digital Corporate Organism (デジタル企業生命体)         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐             │
│  │ Intent  │─────→ │ Frontier │─────→ │ Council  │             │
│  │ (意思)   │      │ (候補)   │      │ (決定)   │             │
│  └──────────┘      └──────────┘      └────┬─────┘             │
│                                            │                    │
│  ┌────────────────────────────────────────┘                    │
│  ↓                                                              │
│  ┌─────────────┐     ┌──────────┐     ┌──────────┐            │
│  │ Execution   │────→│  State   │────→│ Learning │            │
│  │ (実行)      │     │ (状態)   │     │ (学習)   │            │
│  └─────────────┘     └──────────┘     └────┬─────┘            │
│                                             │                   │
│  ┌──────────────────────────────────────────┘                  │
│  ↓                                                              │
│  Intent (更新) ← 投票傾向・進化スコア・実行結果から学習          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 実装要素

### 1. AutonomousCycleResult の拡張

```python
class AutonomousCycleResult(BaseModel):
    cycle_id: int
    objective: OptimizationObjective
    
    # Step AC: 新規
    executive_decision: Optional[ExecutiveDecisionResult] = None
    
    applied_strategies: List[str]
    previous_evolution_score: float
    new_evolution_score: float
    evolution_score_change: float
```

### 2. AutonomousEnterpriseService の更新

自律ループが以下の 9 ステップを実行：

```python
def run_autonomous_cycle(objective):
    # 1. 現在の状態を取得
    current_state = get_current_state()
    
    # 2. シナリオを実行 (Step U)
    run_scenarios()
    
    # 3. 最適化計画を生成 (Step V)
    plan = generate_optimization_plan()
    
    # 4. Pareto Frontier を生成 (Multi-Objective)
    frontier = generate_frontier()
    
    # Step AC: 経営チームが投票
    decision = executive_agents.run_council(frontier)
    
    # 5. 戦略を実行
    new_state = apply_strategies(decision.selected_strategy)
    
    # 6. Intent を学習 (Step AA 強化)
    update_intent_from_decision_and_results(decision, new_state)
    
    # 7. 状態を保存
    save_state(new_state)
    
    return result_with_executive_decision
```

### 3. Intent Learning の強化（3つの学習源）

```python
def update_intent_from_executive_decisions(intent, history):
    """
    3つの学習源から Intent を学習：
    
    1. 選ばれた戦略の ObjectiveVector
       → Intent の重みに反映
    
    2. Executive Agents の投票傾向
       → CFO が毎回「stability」を推す → stability_weight ↑
       → CTO が「innovation」を支持 → innovation_weight ↑
    
    3. 進化スコアの改善度
       → 進化スコアが伸びた戦略方向 → Intent に強化
    """
    
    # 投票パターン分析
    for cycle in history:
        if cycle.executive_decision:
            analyze_agent_votes(cycle.executive_decision)
    
    # 改善度を反映
    improvement_rate = positive_cycles / total_cycles
    learning_confidence = confidence_score(improvement_rate, cycle_count)
    
    # 新 Intent を計算
    return apply_learning(current_intent, learning_history)
```

### 4. Dashboard への統合

新しいセクション：**Executive Decision in Autonomous Loop**

```json
{
  "executive_decision_summary": {
    "selected_candidate_id": "growth_max_growth",
    "aggregated_score": 0.823,
    "top_supporter": "CEO",
    "supporting_roles_count": 4,
    "consensus_level": "high"
  },
  "corporate_intent": {
    "growth_weight": 0.35,
    "profitability_weight": 0.25,
    "innovation_weight": 0.25,
    "stability_weight": 0.15,
    "risk_preference": 0.6,
    "cultural_identity": "innovative"
  }
}
```

## サイクルサマリー例

```
Autonomous Cycle 5: GROWTH
Applied 4 strategies: 新規事業投資, マーケティング拡大, 技術開発, 組織強化

Executive Decision: growth_max_growth
Consensus Level: 4 roles support, 1 opposes
Aggregated Score: 0.823

Evolution: 0.68 → 0.75 (+0.07)

Key Decisions:
- CEO (1.5x): Strongly supports growth strategy
- CFO (1.2x): Concerned about cash reserves, but pragmatic
- CMO (1.0x): Full support for market expansion
- CTO (1.0x): Supports technology acceleration
- CHRO (1.0x): Concerned about org stability
```

## Intent Learning の具体例

### 投票傾向からの学習

| 実行 | CFO投票 | CTO投票 | 進化スコア | 学習結果 |
|------|--------|--------|----------|--------|
| Cycle 1 | 安定性 | 革新性 | ↑0.05 | CFO志向が有効 |
| Cycle 2 | 安定性 | 革新性 | ↑0.07 | CFO志向をさらに強化 |
| Cycle 3 | 安定性 | 革新性 | ↑0.06 | 学習確度↑ |

→ **意思の更新**: `stability_weight` ↑, `innovation_weight` ↑

### 合意度からの学習

| サイクル | コンセンサス | evolution_change | 学習 |
|---------|-----------|-----------------|------|
| 高合意 (CEO + CFO + CMO) | 高 | +0.08 | 合意は高い成果をもたらす |
| 低合意 (CEO のみ) | 低 | +0.02 | 合意の重要性 |

## テスト

| テストファイル | 説明 |
|----------------|------|
| `test_autonomous_loop_with_agents.py` | 自律ループと Executive Agents の統合 |
| `test_intent_learning_with_agents.py` | Intent Learning の強化版 |
| `test_dashboard_autonomous_executive_summary.py` | Dashboard 統合 |

## ドキュメント

- [Corporate Intent Overview](corporate-intent-overview.md) - Intent モデル
- [Executive Agents Overview](executive-agents-overview.md) - 経営チームエージェント
- [Multi-Objective Optimization Overview](multi-objective-optimization-overview.md) - Pareto Frontier

## Step AC 完了時のシステム状態

### 能力

✅ **企業の意思を明示的に定義** (Step AA)
✅ **複数の視点で戦略を評価** (Step AB)
✅ **議論を通じて最適戦略を選択** (Step AC)
✅ **自動的に状態を更新** (Execution)
✅ **投票傾向から学習** (Intent Learning)
✅ **ダッシュボードで進化を可視化**

### システムの特性

🧬 **デジタル企業生命体**の出現：

1. **自律性**: 人間の介入なしに継続的に実行・学習
2. **知性**: 複数の視点から戦略を評価
3. **適応性**: 過去の経験から Intent を進化
4. **透明性**: 全ての決定をダッシュボードで可視化
5. **回復力**: フィードバックループで持続的改善

## 関連ドキュメント

- [Autonomous Loop Overview](autonomous-loop-overview.md)
- [Self-Optimization Overview](self-optimization-overview.md)