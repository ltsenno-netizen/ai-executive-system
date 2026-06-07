# Emergency Playbook API

## GET /api/financials/emergency-playbook

Emergency Playbook の推奨アクションと通知テンプレートを取得します。

### リクエスト

- `notify` (optional): `true` または `false`
  - `true` の場合、Slack / メール通知が発生します。

### レスポンス例

```json
{
  "playbook": {
    "trigger": "cash_below_threshold",
    "cash": 16.9,
    "threshold": 18.0,
    "status": "critical",
    "actions": [
      {"id": "suspend_tranches", "label": "Suspend all pending tranches", "impact": "+2.0"},
      {"id": "reduce_production_cost", "label": "Reduce production cost", "impact": "+0.5"},
      {"id": "pause_advertising", "label": "Pause advertising for 1 month", "impact": "+0.3"},
      {"id": "use_credit_line", "label": "Use credit line", "impact": "+5.0"}
    ],
    "recommended_priority": ["suspend_tranches", "reduce_production_cost", "pause_advertising"]
  },
  "alert_templates": {
    "slack": "...",
    "email_subject": "...",
    "email_body": "..."
  }
}
```

## POST /api/financials/execute-playbook

Emergency Playbook の実行アクションを受け取り、ログ記録のみを行います。

### リクエスト例

```json
{
  "actions": ["suspend_tranches", "reduce_production_cost"]
}
```

### レスポンス例

```json
{
  "status": "executed",
  "executed_actions": ["suspend_tranches", "reduce_production_cost"],
  "timestamp": "2026-04-12T10:00:00Z"
}
```
