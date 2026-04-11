# AI Executive System 完成版：システム全体構造

## 1. システム全体構造

Phase 1〜6 は以下のレイヤーで構成される。

- Phase 1：会社経営モデル（PL / KPI / キャッシュフロー）
- Phase 2：年間オペレーションモデル（部門負荷 / タスク / インシデント）
- Phase 2.5：会社×オペレーション統合（PL とオペレーションの同時シミュレーション）
- Phase 3：中期戦略モデル（KPI ギャップ分析 / 施策提案）
- Phase 4：オペレーション課題モデル（課題検知 / 改善施策 / タスク生成）
- Phase 5：AI 改善ループ（改善履歴 / 効果測定 / 優先度最適化）
- Phase 6：Executive Dashboard（経営ダッシュボード API）

## 2. データフロー

1. `simulate-month-full` で月次 PL とオペレーション状態を生成
2. 現状 KPI をもとに中期戦略ギャップを評価
3. オペレーション課題を検知し、改善施策を選出
4. 改善ループで施策効果を測定し優先度を調整
5. Executive Dashboard が PL / KPI / Ops / Issues / Improvements を統合

## 3. 主要モデル一覧

- `CompanyOperatingModel`
- `AnnualOperationsModel`
- `OperationalIssuesModel`
- `MidtermStrategyModel`
- `ContinuousImprovementState`
- `ExecutiveDashboard`

## 4. 主要サービス一覧

- `CompanyOperatingService`
- `AnnualOperationsService`
- `CompanyOperationsIntegrationService`
- `MidtermStrategyService`
- `OperationalIssuesService`
- `ImprovementCycleService`
- `ExecutiveDashboardService`

## 5. API 一覧

- `GET /api/company/state`
- `GET /api/company/monthly-pl`
- `POST /api/company/simulate-month`
- `POST /api/company/simulate-month-full`
- `GET /api/executive/dashboard?month={month}`
- `GET /api/executive/month/{month}`
- `GET /api/executive/forecast?month={month}`
- `POST /api/improvement/simulate-cycle`
- `GET /api/improvement/history`
- `GET /api/improvement/priority`
- `GET /api/issues`
- `POST /api/issues/detect`
- `POST /api/issues/recommend`
- `POST /api/issues/simulate-month`
- `GET /api/strategy/midterm`
- `POST /api/strategy/gap-analysis`
- `POST /api/strategy/recommend`
- `POST /api/strategy/simulate-year`

## 6. 依存関係と処理順序

- `CompanyOperatingService` と `AnnualOperationsService` が基盤となる
- `CompanyOperationsIntegrationService` が月次統合を提供
- `OperationalIssuesService` が課題検知と改善策を生成
- `ImprovementCycleService` が改善サイクルを回し、優先度状態を更新
- `ExecutiveDashboardService` がすべてを統合し、経営ダッシュボードを構築

## 7. 拡張ポイント

- ML 導入：`ImprovementHistory` を教師データとした優先度推定
- 外部データ連携：Salesforce / ERP / BI から KPI・在庫・ライセンス実績を取り込む
- UI 構築：フロントエンドで `ExecutiveDashboard` を可視化し、ダッシュボード化
- データリセット機能：`initial_state_template.json` を利用した再現性のある初期化
