# Executive Report API

Step G では、月次経営レポートを API で取得できるようにします。

## エンドポイント

### GET /api/reports/latest

最新レポートのメタ情報と Markdown コンテンツを返します。

#### レスポンス例

```json
{
  "period": "2026-04",
  "title": "月次経営レポート 2026年4月",
  "content": "# 月次経営レポート — 2026年4月\n..."
}
```

### GET /api/reports/{year}/{month}

指定した年月のレポートを返します。

#### レスポンス例

```json
{
  "period": "2026-04",
  "title": "月次経営レポート 2026年4月",
  "content": "# 月次経営レポート — 2026年4月\n..."
}
```

### GET /api/reports/history?limit=6

過去のレポート一覧を返します。`limit` は 1〜12 の範囲で指定できます。

#### レスポンス例

```json
[
  {"period": "2026-04", "title": "月次経営レポート 2026年4月"},
  {"period": "2026-03", "title": "月次経営レポート 2026年3月"}
]
```
