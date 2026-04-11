# Phase 3：中期経営計画モデル（Mid-term Strategy Model）

## 目的
ホリプロの3〜5年戦略を仮想的に定義し、会社の現状（PL・オペレーション）とのギャップをAIが自動評価し、改善施策を提案できる「経営企画レイヤー」を構築する。

## 1. 中期戦略テーマ

`data/samples/midterm_strategy_model.json` で定義されたテーマは以下の通り。

- ライセンス比率の引き上げ
- デジタル事業強化
- 公演採算管理強化
- IP開発強化
- 海外展開

各テーマには `target_kpis` が紐づき、目標値が設定される。

## 2. KPI目標の設定方法

`StrategyTheme.target_kpis` で KPI 名と目標値を定義し、現状と比較する。例：

- `license_ratio`: 0.20
- `digital_ratio`: 0.25
- `performance_profit_margin`: 0.15
- `ip_revenue`: 30.0
- `overseas_revenue`: 10.0

## 3. ギャップ分析ロジック

`MidtermStrategyService.evaluate_kpi_gap()` は、現状 KPI と戦略目標を比較し、
`StrategyGap` を生成する。

- `gap = target_value - current_value`
- `severity`: High / Medium / Low
- `current_value` が対象 KPI に存在しない場合は 0.0 と見なす

## 4. 改善施策の提案ロジック

`MidtermStrategyService.recommend_initiatives()` は、ギャップが大きいテーマに紐づく initiative を優先的に提案する。

- `expected_effect` は KPI の加算影響として扱う
- `investment_required` が小さいものを優先して選択

## 5. Phase 2.5 との連携

`MidtermStrategyService.simulate_year_with_strategy()` は、Phase 2.5 の `simulate-month-full` を 1 年分実行し、
年間 KPI を集計する。

### 連携フロー

1. `company_operations_integration_service.simulate_month_full(month)` を 1〜12月で実行
2. 各月の `pl.kpis` を集計して年間 KPI を算出
3. 中期戦略目標とのギャップを分析
4. ギャップに基づき施策提案を生成

## 6. 今後 Phase 4 との統合予定

Phase 4 では、課題モデルの `issue` や `operational risk` と連携し、
戦略ギャップがどの課題から生じているかを分析する予定である。

- `strategy` レイヤーは `operation` レイヤーに改善施策を渡す
- `performance_profit_margin` などの戦略KPIは課題発生条件のトリガーになる
- `recommendation` は `issue` 生成や RACI 施策に展開される
