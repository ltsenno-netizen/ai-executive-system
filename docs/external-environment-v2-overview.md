# External Environment V2 Overview

## 1. 目的

外部環境モデル V2 の目的は、企業が世界の変化に反応する仕組みを強化することです。

- PEST（政治・経済・社会・技術）の変動を企業の業績と意思決定に反映する
- 競合行動が市場シェアや成長率に影響する
- 市場ショック（不況・通貨変動・トレンド変化）が業績に反映される
- 外部環境が CEO、Board、Culture、そして中期計画に連鎖的に影響を与える

この設計により、企業は“世界の変化に反応する”ようになります。

## 2. モデル構造

### PESTFactors

- `political`: 政治リスク・制度の安定性を示す 0.0〜1.0
- `economic`: 景気環境を示す 0.0〜1.0
- `social`: 消費者や社会的潮流の変化
- `technological`: 技術進化・イノベーションの追い風

### CompetitorAction

- `competitor_name`: 競合企業名
- `aggressiveness`: 競合の攻め度合い 0〜1
- `market_share_shift`: 市場シェア変化の影響 ±%
- `notes`: 説明

### MarketShock

- `shock_type`: `recession` / `currency` / `trend_shift` など
- `severity`: 衝撃の強さ 0〜1
- `duration_months`: 継続期間（複数月）
- `description`: 説明

### ExternalEnvironmentState

- `period`: 期間（例: 2026-01）
- `pest`: PEST 要因
- `competitors`: 競合アクション
- `shocks`: 発生中の市場ショック
- `market_growth_modifier`: 事業成長率補正
- `risk_modifier`: CEO / Board のリスク評価に影響する補正

## 3. 外部環境エンジン

### 3.1 PEST の変動ロジック

- `economic`: ランダムウォーク ±0.05
- `technological`: 緩やかに上昇
- `social`: トレンド変化で揺れる
- `political`: ショック時に急変

### 3.2 競合行動

- 高い `aggressiveness` を持つ競合は市場成長を抑制し、企業の `risk_modifier` を押し上げる
- 競合攻勢が高いと CEO の攻め意欲に影響する

### 3.3 市場ショック

- `recession`: `market_growth_modifier` を低下させ、`risk_modifier` を上げる
- `currency`: 円安 / 為替変動はコスト影響として扱い、成長補正を調整する
- `trend_shift`: 成長ターゲットをシフトさせ、特定事業に +0.1 の成長補正を与える

## 4. 企業への影響

### 4.1 PL / KPI への影響

- `market_growth_modifier` は事業成長を乗算して月次 PL に反映
- `currency` shock は原価率を上昇させる
- `recession` は興行・広告売上を減少させる

### 4.2 CEO への影響

- `economic` が低いと CEO の `risk_tolerance` を下げる
- `technological` が高いと `innovation` 案を優先する
- 競合 `aggressiveness` が高いと CEO の攻撃性が高まる

### 4.3 Board への影響

- `recession` は RiskDirector をより保守的にする
- 競合攻勢は BrandDirector を攻め案支持に傾ける

### 4.4 Culture への影響

- `recession` は `stability_culture` を高める
- `technological` は `innovation_culture` を高める

## 5. データフロー

1. `monthly_batch_service` が新規環境を生成し保存する
2. 生成環境は月次シミュレーションに渡される
3. `company_operating_service` は `market_growth_modifier` とショックを PL に適用する
4. `AICeoAgent` と `AIBoardAgent` は環境を受け取り判断を調整する
5. `CultureEngine` は環境を文化に反映する
6. `executive_dashboard_service` は最新環境を集約して表示する

## 6. ダッシュボード表示例

- `economic`: 0.45
- `competitor_pressure`: 1.0
- `shock_summary`: ["recession", "currency"]

外部環境サマリーは、経営判断を支えるリスク・成長トレンドの可視化を目的としています。
