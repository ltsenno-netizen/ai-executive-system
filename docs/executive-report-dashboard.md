# Executive Report Dashboard

Step G-1 では、ダッシュボードに「Executive Reports」タブを追加し、月次レポートの最新表示と履歴一覧を提供します。

## タブ構成

- Executive Summary
- Meetings
- Narrative
- Reports ← NEW

## Reports タブ内容

### 1. Latest Report

- Period: 2026-04
- Title: 月次経営レポート — 2026年4月
- Summary: 4月は市場ショックと投資判断が重なり、守りと攻めのバランスが問われた月だった…
- [Open Report]

### 2. Report History

- 2026-03 — 月次経営レポート — 2026年3月
  - Summary: 市場回復の兆しが見え始め、投資判断が…
  - [Open]

- 2026-02 — 月次経営レポート — 2026年2月
  - Summary: 組織負荷が高まり、実行力スコアが…
  - [Open]

## バックエンド連携

### 必要なダッシュボードモデル

- latest_report_period: Optional[str]
- latest_report_title: Optional[str]
- latest_report_summary: Optional[str]
- reports: List[ReportSummary]

### ReportSummary モデル

- period: str
- title: str
- summary: str

### API レスポンス例

```json
{
  "latest_report_period": "2026-04",
  "latest_report_title": "月次経営レポート — 2026年4月",
  "latest_report_summary": "4月は市場ショックと投資判断が重なり…",
  "reports": [
    {
      "period": "2026-04",
      "title": "月次経営レポート — 2026年4月",
      "summary": "4月は市場ショックと投資判断が…"
    },
    {
      "period": "2026-03",
      "title": "月次経営レポート — 2026年3月",
      "summary": "市場回復の兆しが見え始め…"
    }
  ]
}
```

## UI 側想定データ構造

- dashboard.latest_report_period
- dashboard.latest_report_title
- dashboard.latest_report_summary
- dashboard.reports[]

## データフロー

1. `ExecutiveDashboardService.build_dashboard(month)` が呼び出される
2. `ExecutiveReportService.get_latest_report()` で最新レポートのメタ情報を取得
3. `ExecutiveReportService.list_reports(limit=6)` で履歴を取得
4. `ExecutiveDashboard` に latest_report_* と `reports` を埋め込む

## サービスフロー

- `ExecutiveReportService.list_reports(limit=6)` を呼び出し
- 最新レポートのメタ情報とサマリをダッシュボードモデルに埋め込む
- レポートが存在しない場合は `null` / `[]` を返す

## API 利用

ダッシュボード UI では以下を使用します。

- `GET /api/reports/latest`
- `GET /api/reports/{year}/{month}`
- `GET /api/reports/history?limit=N`

## テスト要件

- 最新レポートがダッシュボードに含まれる
- reports 履歴が返る
- レポート未生成時にフォールバックする
