# Enterprise Evolution Overview

## 進化モデルの概要

Enterprise Evolution Model は、文化 × 外部環境 × 経営チームの相互作用を統合的に計算するシステムです。これにより、企業が長期的に「進化」する複雑系のフィードバックループを実現します。

## 文化 × 外部環境 × 経営チームの相互作用

### 1. 外部環境 → 文化への影響
- **不況時**: stability_culture +0.02 (安定志向が強まる)
- **技術革新時**: innovation_culture +0.03 (革新性が促進される)
- **競合の攻撃性が高い場合**: aggressiveness_culture +0.02 (競争意識が高まる)

### 2. 文化 → 経営チームへの影響
- **brand_culture が高い場合**: CMO の brand_focus +0.05
- **people_culture が高い場合**: CHRO の people_focus +0.05
- **cost_culture が高い場合**: CFO の financial_focus +0.05

### 3. 経営チーム → 文化への逆影響
- **CFO が保守的な場合**: risk_aversion_culture +0.02
- **COO が execution-heavy の場合**: execution_culture +0.03
- **CMO が攻め型の場合**: aggressiveness_culture +0.02

### 4. Board → 文化への影響
- **RiskDirector が反対しがちな場合**: stability_culture +0.01
- **BrandDirector が攻め案を支持する場合**: brand_culture +0.02

## evolution_score の意味

evolution_score は企業がどれだけ「変化したか」を数値化した指標です。

```
evolution_score = (culture_shift_total * 0.4) + (leadership_shift_total * 0.3) + (environment_pressure * 0.3)
```

- **culture_shift_total**: 文化の変化量の合計
- **leadership_shift_total**: 経営チームの変化量の合計
- **environment_pressure**: 外部環境の圧力度

スコアが高いほど、企業が積極的に変化していることを示します。

## ダッシュボード統合

Executive Dashboard に Enterprise Evolution Summary が表示されます：

- **evolution_score**: 進化スコア
- **environment_pressure**: 外部環境の圧力
- **culture_shift**: 文化の変化内容
- **leadership_shift**: 経営チームの変化内容

## 長期的な企業進化の例

### ケース1: 安定成長期
- 外部環境: 穏やか
- 文化: バランス型
- 経営チーム: 安定志向
- 結果: evolution_score が低く、安定した成長

### ケース2: 危機対応期
- 外部環境: 不況 + 競合激化
- 文化: コスト重視 + 安定志向
- 経営チーム: CFO が保守的
- 結果: evolution_score が高く、企業が大きく変化

### ケース3: 革新期
- 外部環境: 技術革新
- 文化: イノベーション重視
- 経営チーム: CMO が攻め型
- 結果: evolution_score が高く、積極的な進化

このモデルにより、企業は外部環境の変化に適応し、文化と経営チームが相互に影響し合いながら、長期的に進化していきます。