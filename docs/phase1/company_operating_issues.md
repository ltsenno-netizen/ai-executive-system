# Phase 1：会社経営モデル GitHub Issues

以下は Phase 1 の実装に対応する課題リストです。GitHub Issue としてそのまま起票できる形式でまとめています。

## Issue: 年間PLモデルの実装
- 目的: 12ヶ月の年間PLモデルを `MonthlyPL` で定義し、売上、費用、利益、利益率、キャッシュフローを扱えるようにする。
- 参照: `src/backend/app/models/company_operating_model.py`
- 成果物: `company_operating_model.json` を読み込み可能なデータモデル

## Issue: 季節性パラメータの実装
- 目的: `SeasonalityFactor` を実装し、月別の売上・費用に季節要因を適用する。
- 参照: `src/backend/app/services/company_operating_service.py`
- 成果物: 7〜9月公演、10〜12月CM・広告、11〜12月MD などの季節性反映

## Issue: 投資計画ロジックの実装
- 目的: 投資計画を `InvestmentPlan` で定義し、月次キャッシュフローに投資額を反映する。
- 参照: `src/backend/app/services/company_operating_service.py`
- 成果物: デジタル、IP、海外投資の月次支出反映

## Issue: KPI計算ロジックの実装
- 目的: `CompanyKPI` を用いてライセンス比率、デジタル比率、タレントLTV、営業利益、キャッシュ残高を算出する。
- 参照: `src/backend/app/services/company_operating_service.py`
- 成果物: 月次KPIの自動更新

## Issue: 月次シミュレーションAPIの実装
- 目的: `POST /api/company/simulate-month` を実装し、指定月のPL・キャッシュ・KPIを返却する。
- 参照: `src/backend/app/routes/company_operating.py`
- 成果物: 月次シミュレーションのAPI化

## Issue: E2Eテスト（1年分のシミュレーション）
- 目的: 12ヶ月分のシミュレーションを通して Seasonality、投資、キャッシュフロー、KPI の整合性を検証する。
- 参照: `test_company_operating.py`
- 成果物: 1年シミュレーションの自動検証
