# Phase 4：オペレーション課題モデル（Operational Issues Model）

## 目的
会社の運営状態（PL・オペレーション・戦略）を自動的に解析し、課題を検知して改善施策を生成し、部門タスクに落とし込む「経営改善AIレイヤー」を構築する。

## 1. 課題モデルの構造

`src/backend/app/models/operational_issues_model.py` には以下の構造が定義される。

- `IssueDefinition`
  - `id`: 課題を一意に識別する文字列
  - `name`: 課題名
  - `description`: 課題の説明
  - `detection_rules`: KPI や負荷指標の閾値マップ
  - `severity`: Critical / High / Medium / Low
  - `related_departments`: 関連部門リスト

- `IssueInstance`
  - `id`: 課題インスタンス ID
  - `issue_id`: 元の課題定義 ID
  - `month`: 該当月
  - `detected_values`: 検知された値
  - `severity`: 課題の重大度
  - `status`: Open / InProgress / Resolved
  - `recommended_actions`: 推奨アクション名リスト

- `ImprovementAction`
  - `id`: 改善施策 ID
  - `issue_id`: 紐づく課題 ID
  - `name`: 改善施策名
  - `description`: 改善施策の説明
  - `owner_department`: 所管部門
  - `expected_effect`: KPI 改善見込み
  - `task_template_id`: タスクテンプレート ID

- `OperationalIssuesModel`
  - `issues`: `IssueDefinition` のリスト
  - `actions`: `ImprovementAction` のリスト

## 2. 検知ロジック

`OperationalIssuesService.detect_issues()` は、Phase 2.5 の `simulate_month_full()` から得た `monthly_state` と Phase 1 の `company_kpis` を元に、`detection_rules` を評価して課題を検知する。

- 値が閾値を上回る場合と下回る場合を柔軟に判定
- `duplicate_revenue_entries`、`license_processing_days`、`missing_kpi_count` は大きいほど問題
- `performance_profit_margin`、`inventory_turnover`、`allocation_accuracy` は小さいほど問題

検知結果は `IssueInstance` として返却される。

## 3. 改善施策生成ロジック

`OperationalIssuesService.generate_recommendations()` は、検知された課題に紐づく `ImprovementAction` を抽出して返す。

- 1 つの課題に複数の施策を紐づけられる
- 将来的に施策の優先順位付けや AI 学習を追加可能

## 4. タスクへの落とし込み

`OperationalIssuesService.convert_actions_to_tasks()` は、改善施策の `task_template_id` を元に `TaskInstance` を生成する。

- `owner_department` によって担当部門を設定
- `task_template_id` があればテンプレート連携を想定
- `expected_effect` を保持して効果見込みを可視化

## 5. Phase 2.5 との連携

`OperationalIssuesService.simulate_month_with_issues()` は以下を一括実行する。

1. `CompanyOperationsIntegrationService.simulate_month_full(month)` を呼び出す
2. 課題検知を実行
3. 推奨改善施策を生成
4. タスクを生成

返却構造例:

- `month`
- `pl`
- `operations`
- `issues`
- `recommendations`
- `generated_tasks`

## 6. Phase 5 への布石

Phase 5 では、課題検知結果と改善施策の効果を AI がフィードバックループで学習し、
自動的に閾値や優先順位を調整する設計を想定している。

- `IssueInstance.status` の変化を学習データとする
- `expected_effect` と実績の差分をモデル化
- 課題検知ルールの自動最適化をフェーズ 5 で追加可能
