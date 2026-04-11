# AI Executive System Demo Scenarios

## シナリオ1：公演ピーク → 課題発生 → 改善 → KPI改善

1. `POST /api/company/simulate-month-full` で `month=7` を実行
2. `issues` に `weak_performance_profit_margin` が検知される
3. 改善施策 `公演採算レビュー会議の定例化` を確認
4. `POST /api/improvement/simulate-cycle` で `month=7` を実行
5. 8月の KPI が改善したか、`profit_margin` と `performance_profit_margin` を確認

## シナリオ2：ライセンス比率低下 → 戦略施策 → 次月改善

1. `POST /api/company/simulate-month-full` で `month=7` を実行
2. `strategy` / KPI に `license_ratio` の低下が確認される
3. `POST /api/strategy/recommend` で `month=7` を実行し、戦略施策を取得
4. `POST /api/improvement/simulate-cycle` で `month=7` を実行
5. `GET /api/executive/dashboard?month=8` で `license_ratio` の上昇を確認

## シナリオ3：MD在庫リスク → タスク生成 → 効果測定

1. `POST /api/company/simulate-month-full` で `month=7` を実行
2. `issues` に `md_inventory_risk` が検知される
3. `POST /api/issues/recommend` で `month=7` を実行し、`inventory_optimization` を取得
4. `POST /api/improvement/simulate-cycle` で `month=7` を実行
5. `GET /api/executive/dashboard?month=8` で `inventory_turnover` の改善と生成タスクを確認
