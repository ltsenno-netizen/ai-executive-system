# Phase 8：外部環境モデル（Industry & Market Model）

## 目的
エンタメ業界・市場・競合・トレンド・ショックなどの外部環境をモデル化し、会社の PL・KPI・戦略・課題・改善に影響を与える「世界側のレイヤー」を構築する。

## 1. モデル構造

- `MarketSegment`
- `IndustryTrend`
- `Competitor`
- `ExternalShock`
- `ExternalEnvironmentModel`

## 2. MarketSegment

- `base_size`: 市場規模
- `growth_rate`: 年成長率
- `seasonality`: 月別係数

例: 舞台市場、CM 広告市場、デジタル配信市場、MD 市場

## 3. IndustryTrend

- 外部トレンドが各市場に与える影響
- 例: `デジタルシフト`、`ライブ回帰`

## 4. Competitor

- 各競合の市場強さと攻勢レベル
- `competition_pressure` を算出してシェア獲得難易度に活用

## 5. ExternalShock

- 期間限定の外部ショック
- 例: `パンデミック`、`景気後退`、`法規制変更`

## 6. 市場規模の計算式

`market_size = base_size × (1 + growth_rate)^(year_offset) × seasonality × trend_factor × shock_factor`

- `year_offset`: 基準年 2026 からの差分
- `trend_factor`: 全トレンドの市場影響合計
- `shock_factor`: 発動中ショックの影響合計

## 7. 会社モデルへの影響

### PL への影響
- `apply_external_environment_to_pl()` で市場規模と競争圧を元に売上ポテンシャルを調整

### KPI への影響
- `apply_environment_to_kpis()` で `license_ratio` や `digital_ratio` などを外部環境に応じて補正

### 課題への影響
- 市場縮小は新たな課題トリガーとなり、改善サイクルに反映
- 市場成長は投資機会として戦略側に活用

## 8. 「世界の変化に反応する企業」

- 外部モデルを導入すると、企業は「市場の変化によって成長・課題が変化する」動的な組織になる
- 実際に業界レポートや競合動向データに差し替えることで、よりリアルな経営デジタルツインになる
