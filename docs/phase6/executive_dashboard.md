# Phase 6：AI Executive Dashboard（経営ダッシュボード）

## 目的
Phase 1〜5 の全データを統合し、経営者が会社の状態を一目で把握できる Executive Dashboard API を構築する。

## 1. Executive Dashboard の目的

- PL の収益・コスト・利益・キャッシュ状況を可視化
- KPI（license_ratio, digital_ratio など）を月次で把握
- 部門負荷と現行タスク・インシデント状況を把握
- 課題検知結果と改善施策実行状況を表示
- 次月の予測を提供し、意思決定を支援

## 2. サマリー構造

- `ExecutivePLSummary`
- `ExecutiveKPISummary`
- `ExecutiveOpsSummary`
- `ExecutiveIssueSummary`
- `ExecutiveImprovementSummary`
- `ExecutiveDashboard`

## 3. API 利用例

- `GET /api/executive/dashboard?month=7`
- `GET /api/executive/month/7`
- `GET /api/executive/forecast?month=7`

## 4. 各 Summary の説明

- `PL`: 収益・コスト・利益・利益率・キャッシュ残高
- `KPI`: 月次 KPI の一覧
- `Operations`: 部門負荷、アクティブタスク数、インシデント数
- `Issues`: 現在検知された課題サマリー
- `Improvements`: 改善施策の実行履歴と優先度

## 5. 今後の拡張

- フロントエンド UI との連携
- BI ツール向け CSV / JSON エクスポート
- KPI トレンド分析と異常検知表示
- 予測の精度向上と機械学習モデル連携
