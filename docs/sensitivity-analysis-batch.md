# Sensitivity Analysis Batch

## 実行方法

```bash
python run_sensitivity_batch.py --small-set
```

`--small-set` を指定すると、2x2x1x1 の小規模セットを実行します。

## 出力

- `sensitivity_outputs/scenario_<params>_monthly.csv`
- `sensitivity_outputs/scenario_<params>_summary.json`

## パラメータ

- `max_investment_pct_of_cash`: 0.10〜0.35
- `minimum_cash_threshold`: 2.0〜5.0
- `shock_strength`: -0.10〜-0.40
- `shock_duration`: 1〜6

## 設定

`run_sensitivity_batch.py` は内部で以下を実行します。

- `CompanyOperationsIntegrationService.simulate_month_full(...)`
- `ExternalEnvironmentService.build_environment_state(...)`
- `FinancialService.evaluate_investment_request(...)`

## テスト

```bash
python -m unittest tests.test_sensitivity_batch
```
