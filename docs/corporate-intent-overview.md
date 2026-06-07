# Corporate Intent（企業の意思）概要

## 什么是 Corporate Intent

Corporate Intent は、企業の「意思」を明示的なデータモデルとして定義する機能です。企業が何を優先し、どのような価値観で意思決定を行い、どのトレードオフを許容するかを体系化します。

## コアコンセプト

### 1. 優先目的的重み

| 重み | 説明 | 範囲 |
|------|------|------|
| `growth_weight` | 成長重視度 | 0.0 - 1.0 |
| `profitability_weight` | 収益性重視度 | 0.0 - 1.0 |
| `innovation_weight` | 革新性重視度 | 0.0 - 1.0 |
| `stability_weight` | 安定性重視度 | 0.0 - 1.0 |

> **重要**: 4つの重みの合計は自動的に正規化され、1.0になります。

### 2. リスク選好と時間軸

| パラメータ | 説明 | 範囲 |
|------------|------|------|
| `risk_preference` | リスク選好度 | 0=超保守, 1=超攻め |
| `time_horizon` | 時間軸 | 0=短期, 1=長期 |

### 3. 企業文化的アイデンティティ

```python
cultural_identity: str  # "innovative", "stable", "aggressive", "conservative", "balanced"
```

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Corporate Intent                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Model      │  │   Engine     │  │   Service    │      │
│  │  Layer       │  │   Layer      │  │   Layer     │      │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤      │
│  │Corporate     │  │score_        │  │get_intent()  │      │
│  │Intent        │  │candidate()   │  │save_intent() │      │
│  │              │  │              │  │              │      │
│  │IntentScore   │  │select_       │  │update_       │      │
│  │              │  │strategy()    │  │intent()      │      │
│  │Intent        │  │              │  │              │      │
│  │Alignment     │  │rank_         │  │select_       │      │
│  │              │  │candidates()  │  │optimal()     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           ▼                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    API Layer                         │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ GET  /api/intent                    → 意思取得       │   │
│  │ POST /api/intent/set                → 意思設定       │   │
│  │ POST /api/intent/update             → 学習更新       │   │
│  │ GET  /api/intent/analysis          → 詳細分析       │   │
│  │ GET  /api/intent/optimal-strategy  → 最適戦略       │   │
│  │ GET  /api/intent/ranked-strategies → 戦略ランクリスト│   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Intent Scoring アルゴリズム

### 基本スコア計算

```python
base_score = (
    intent.growth_weight * vector.growth +
    intent.profitability_weight * vector.profitability +
    intent.innovation_weight * vector.innovation +
    intent.stability_weight * vector.stability
)
```

### リスク調整

```python
if intent.risk_preference > 0.5:
    # 攻め志向：リスク取得をボーナスに
    risk_adjustment = 1.0 + (risk_preference * risk_level * 0.15)
else:
    # 保守志向：リスク回避をボーナスに
    risk_adjustment = 1.0 + ((1.0 - risk_preference) * stability * 0.15)
```

### 時間軸調整

```python
if intent.time_horizon > 0.5:
    # 長期志向：革新と安定を強化
    time_horizon_adjustment = 1.0 + (time_horizon * innovation * 0.1)
else:
    # 短期志向：成長と収益性を強化
    time_horizon_adjustment = 1.0 + ((1.0 - time_horizon) * (growth + profitability) * 0.05)
```

### 最終スコア

```python
final_score = base_score * risk_adjustment * time_horizon_adjustment
```

## Intent Learning（企業の意思の学習）

企業が過去に選択した戦略から、意思を逆推定する機能です。

### 学習プロセス

1. **履歴取得**: 過去の Autonomous Cycle 結果を取得
2. **平均計算**: 選択された戦略の目的ベクトル平均を計算
3. **重み更新**: 正規化して Intent に反映
4. **信頼度計算**: 学習の信頼度を算出

```python
def update_intent_from_history(intent, history):
    avg_growth = mean(h.vector.growth for h in history)
    avg_profit = mean(h.vector.profitability for h in history)
    avg_innov = mean(h.vector.innovation for h in history)
    avg_stab = mean(h.vector.stability for h in history)
    
    # 正規化して反映
    total = avg_growth + avg_profit + avg_innov + avg_stab
    return CorporateIntent(
        growth_weight=avg_growth / total,
        ...
    )
```

## ダッシュボード統合

```python
class CorporateIntentSummary(BaseModel):
    growth_weight: float
    profitability_weight: float
    innovation_weight: float
    stability_weight: float
    risk_preference: float
    time_horizon: float
    cultural_identity: str
```

## 使用例

### 1. 意思の取得

```bash
GET /api/intent
```

```json
{
  "growth_weight": 0.35,
  "profitability_weight": 0.25,
  "innovation_weight": 0.25,
  "stability_weight": 0.15,
  "risk_preference": 0.6,
  "time_horizon": 0.7,
  "cultural_identity": "innovative"
}
```

### 2. 意思の設定

```bash
POST /api/intent/set
```

```json
{
  "growth_weight": 0.4,
  "profitability_weight": 0.3,
  "innovation_weight": 0.2,
  "stability_weight": 0.1,
  "risk_preference": 0.7,
  "time_horizon": 0.8,
  "cultural_identity": "aggressive"
}
```

### 3. 学習による更新

```bash
POST /api/intent/update
```

```json
{
  "message": "Intent updated from learning history",
  "intent": { ... },
  "learning_confidence": 0.85
}
```

### 4. 最適戦略の取得

```bash
GET /api/intent/optimal-strategy
```

```json
{
  "message": "Optimal strategy selected based on Intent",
  "strategy": {
    "scenario_type": "growth",
    "optimization_objective": "max_growth",
    "objective_vector": { ... }
  },
  "score": {
    "candidate_id": "growth_max_growth",
    "score": 0.823,
    "breakdown": { ... }
  }
}
```

## テスト

| テストファイル | 説明 |
|----------------|------|
| `test_corporate_intent_engine.py` | Intent Engine のユニットテスト |
| `test_corporate_intent_service.py` | サービス層のテスト |
| `test_corporate_intent_api.py` | API エンドポイントのテスト |
| `test_dashboard_corporate_intent_summary.py` | ダッシュボード統合テスト |

## 関連ドキュメント

- [Multi-Objective Optimization Overview](multi-objective-optimization-overview.md)
- [Self-Optimization Overview](self-optimization-overview.md)
- [Autonomous Loop Overview](autonomous-loop-overview.md)