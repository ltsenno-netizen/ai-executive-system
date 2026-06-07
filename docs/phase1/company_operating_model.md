# Phase 1：会社経営モデル（Company Operating Model）

## 目的
年間PL、季節性、キャッシュフロー、月次イベント、経営KPIを実装し、えみプロ150億モデルを「年間で動く会社」として再現する。

## 1. 年間PLモデルの説明

`src/backend/app/models/company_operating_model.py` では以下のモデルを定義する。

- `MonthlyPL`
  - `month`: 1〜12
  - `revenue`: 売上源別（`talent`, `performance`, `license`, `md`）
  - `cost`: 費用項目別（`talent_related`, `production`, `sg&a`, `digital_investment`, `other`）
  - `profit`, `profit_margin`, `cash_flow`
- `SeasonalityFactor`
  - `month`
  - `revenue_multiplier`
  - `cost_multiplier`
- `InvestmentPlan`
  - `category`, `amount`, `start_month`, `end_month`, `expected_return_rate`
- `CompanyKPI`
  - `gross_profit`, `operating_profit`, `cash_balance`, `license_ratio`, `digital_ratio`, `talent_ltv_index`
- `CompanyOperatingModel`
  - `fiscal_year`, `monthly_pl`, `seasonality`, `investments`, `kpis`

## 2. 季節性パラメータ一覧

`data/samples/company_operating_model.json` に定義された季節性は次の通り。

- `公演`: 7〜9月 1.3倍
- `CM・広告`: 10〜12月 1.4倍
- `MD`: 11〜12月 1.5倍
- `契約更新`: 1〜3月に `talent_related` 費用が 1.05倍（後続フェーズで負荷・タスク生成につなぐ）

## 3. 投資計画

実装済み投資計画は以下。

- `digital`: 年間 10億円（1〜12月均等）
- `IP開発`: 年間 5億円（4〜9月）
- `海外展開`: 年間 2億円（10〜12月）

各月の投資額は `CompanyOperatingService.calculate_cash_flow()` で算出され、キャッシュ残高として反映される。

## 4. KPI定義

`CompanyKPI` では次の指標を管理する。

- `gross_profit`: 売上 － 直接費用（タレント関連・制作費）
- `operating_profit`: 売上 － 総費用
- `cash_balance`: 月次キャッシュ残高
- `license_ratio`: ライセンス売上比率
- `digital_ratio`: デジタル関連指標（初期値 13%）
- `talent_ltv_index`: タレントLTV指標（初期値 1.0）

## 5. シミュレーションロジック

`src/backend/app/services/company_operating_service.py` の主な処理は以下。

1. `load_company_model()` で JSON を読み込み
2. `apply_seasonality()` で売上と費用に季節性を適用
3. `calculate_monthly_pl()` で月次 PL を算出
4. `calculate_cash_flow()` で投資計画を反映し、キャッシュ残高を更新
5. `calculate_kpis()` で KPI を計算
6. `simulate_month()` で任意月をシミュレーション

### 返却値
`simulate_month()` は以下を返す。

- `month`
- `revenue`
- `cost`
- `profit`
- `profit_margin`
- `cash_flow`
- `cash_balance`
- `kpis`

## 6. API一覧

- `GET /api/company/state`
  - 会社全体の年間モデルを返す
- `GET /api/company/monthly-pl`
  - 12ヶ月分の月次PLを返す
- `POST /api/company/simulate-month`
  - リクエスト例: `{ "month": 7 }`

## 7. 今後のフェーズ連携

Phase2 では年間イベントと部門負荷を導入し、`1〜3月契約更新` や `7〜9月公演ピーク` を部門タスクに変換する。

Phase3 では中期戦略と連携し、中期KPIを目標値として扱う。

Phase4 では運用課題を検出し、キャッシュ・PL・KPIの変動要因を課題トリガーとして利用する。

## 8. 実装確認項目

- 年間 150 億モデルが 12 か月に分配されている
- 季節性が正しく適用されている
- 投資計画がキャッシュフローに反映されている
- 月次シミュレーションで KPI が返却される
- 後続フェーズで `talent_ltv_index` が更新可能な設計になっている
