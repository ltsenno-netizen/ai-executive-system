# Phase 5：AI改善ループ（AI-driven Continuous Improvement）

## 目的
課題検知から改善施策の実行、効果測定、優先度最適化までを AI が自律的に回す「継続的改善エンジン」を構築する。

## 1. 改善ループの全体構造

`src/backend/app/services/improvement_cycle_service.py` は、以下の流れで 1 サイクルを実行する。

1. `simulate-month-full(month)` を実行
2. `detect_issues()` で課題を検知
3. `recommend_actions()` で改善施策を抽出
4. `select_actions_by_priority()` で優先度順に施策を選択
5. `convert_actions_to_tasks()` でタスクを生成
6. `simulate-month-full(month + 1)` を実行
7. `evaluate_action_effectiveness()` で効果を測定
8. `update_action_priority()` で priority_score を更新
9. `ContinuousImprovementState` を保存

## 2. モデル構造

- `ImprovementHistory`
  - `id`
  - `month`
  - `issue_id`
  - `action_id`
  - `expected_effect`
  - `actual_effect`
  - `effect_error`
  - `priority_score`

- `ActionEffectiveness`
  - `action_id`
  - `total_runs`
  - `avg_effect`
  - `avg_error`
  - `updated_priority`

- `ContinuousImprovementState`
  - `month`
  - `executed_actions`
  - `updated_priorities`
  - `action_effectiveness`

## 3. expected_effect と actual_effect の比較方法

- `actual_effect` は `前月 KPI` から `今月 KPI` への差分を算出する。
- `effect_error` は `expected_effect - actual_effect` の差を取る。
- 期待値が負の指標（例: `license_processing_days`）でも正しく評価できる。

## 4. priority_score の更新ロジック

- 施策の効果と誤差を比べて、優先度を動的に調整する。
- `priority_score = priority_score + (effectiveness - error) * weight`
- 結果は `0.1〜5.0` でクリップされる。

## 5. 施策選択の考慮点

- `select_actions_by_priority()` は、課題に紐づく施策を優先度順に選出する。
- 高度な負荷・投資額評価は今後の拡張として、現状は優先度スコアと課題重大度を組み合わせて選択する。

## 6. Phase 4 までの統合

- Phase 4 の `OperationalIssuesService` による課題検知と改善策生成をそのまま活用する。
- Phase 5 は `OperationalIssuesService` の上位レイヤーとして機能し、履歴と優先度を蓄積する。

## 7. 将来の拡張ポイント

- ML モデル導入時には、`ImprovementHistory` の蓄積データを教師データとして利用できる。
- `ActionEffectiveness` をベースに学習済み優先度や施策精度を生成することが可能。
- 部門負荷・投資対効果を追加することで、より高度な施策選択が可能になる。
