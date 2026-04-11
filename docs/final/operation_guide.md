# AI Executive System 運用ガイド

## 1. 月次シミュレーションの回し方

### 1.1 simulate-month-full の使い方

- エンドポイント: `POST /api/company/simulate-month-full`
- パラメータ: `{ "month": 7 }`
- 返却: PL、オペレーション、戦略サマリー

### 1.2 月次 PL・部門負荷・課題の読み方

- `pl` では収益・コスト・利益・利益率・キャッシュ残高を確認
- `operations` では部門ごとの負荷、生成タスク数、インシデント数を確認
- `issues` では検知された課題と関連部門、重要度を確認

## 2. 年間シミュレーションの回し方

### 2.1 1〜12月をループするサンプルコード

```python
from app.services.company_operations_integration_service import CompanyOperationsIntegrationService

service = CompanyOperationsIntegrationService()
for month in range(1, 13):
    result = service.simulate_month_full(month)
    print(f"Month {month}: profit={result['pl']['profit']}, tasks={len(result['operations']['generated_tasks'])}")
```

### 2.2 年間 KPI の読み方

- 各月の `pl.kpis` を比較し、トレンドを把握
- `license_ratio`, `digital_ratio`, `performance_profit_margin` などが戦略指標

## 3. 改善ループの使い方

### 3.1 simulate-cycle の使い方

- エンドポイント: `POST /api/improvement/simulate-cycle`
- パラメータ: `{ "month": 7 }`
- フロー: 7月の課題検知 → 施策選択 → 8月の効果測定 → 優先度更新

### 3.2 expected_effect と actual_effect の比較方法

- `expected_effect` は施策の見込み改善値
- `actual_effect` は前月 KPI から翌月 KPI までの実績差分
- `effect_error = expected_effect - actual_effect`

### 3.3 priority_score の意味

- 施策の過去効果に応じて優先度を動的に変化させる
- `0.1〜5.0` の範囲でクリップされ、将来的な施策選択に影響

## 4. ダッシュボードの読み方

### 4.1 PL カード

- 収益、コスト、利益、利益率、キャッシュ残高を経営者視点で表示

### 4.2 KPI カード

- 主要 KPI の月次値を確認し、戦略目標とのギャップを把握

### 4.3 部門負荷ヒートマップ

- `department_load` の負荷分布から部門ごとのリソース状態を確認

### 4.4 課題一覧

- `issues` には検知された課題の ID、重要度、関連部門を表示

### 4.5 改善施策履歴

- 実行済み施策の `executed_actions` を確認し、期待値と実績を比較

### 4.6 優先度ランキング

- `updated_priorities` により、次回注力すべき施策を判断

### 4.7 次月予測

- `forecast` では `simulate-month-cycle` の結果をベースに、次月の改善効果を予測

## 5. 戦略の更新方法

### 5.1 `midterm_strategy_model.json` の編集方法

- `data/samples/midterm_strategy_model.json` を編集する
- 各 `theme` に `target_kpis` と `initiatives` を追加

### 5.2 KPI 目標の変更

- `target_kpis` の値を変更すると、ギャップ分析結果が変わる

### 5.3 新規施策の追加

- `initiatives` に `name`, `description`, `expected_effect`, `investment_required` を追加
- 追加後は `POST /api/strategy/recommend` で提案候補に反映される
