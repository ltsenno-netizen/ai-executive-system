# Step B: Emergency Playbook & Notification Integration 実装指示書

## 目的

Downside や Simultaneous シナリオで明らかになったように、キャッシュが閾値を割る瞬間に即応できる仕組みが必要です。

Step B では以下を実現します。

- 緊急プレイブック（Emergency Playbook）生成機能の拡張
- Slack / メール通知フックの追加
- ダッシュボードへの Emergency パネル統合
- プレイブック実行 API の追加（ログ記録のみ）

---

## 1. バックエンド実装

### 1.1 対象ファイル

- `src/backend/app/services/financial_service.py`
- `src/backend/app/routes/financial.py`
- `src/backend/app/services/executive_dashboard_service.py`
- `src/backend/app/services/notification_service.py`（新規）
- `data/samples/emergency_playbook_templates.json`（新規）

### 1.2 Emergency Playbook の仕様

既存の `generate_emergency_playbook(financials, market_state, org_state)` を拡張します。

出力例:

```json
{
  "trigger": "cash_below_threshold",
  "cash": 16.9,
  "threshold": 18.0,
  "actions": [
    {"id": "suspend_tranches", "label": "Suspend all pending tranches", "impact": "+2.0"},
    {"id": "reduce_production_cost", "label": "Reduce production cost", "impact": "+0.5"},
    {"id": "pause_advertising", "label": "Pause advertising for 1 month", "impact": "+0.3"},
    {"id": "use_credit_line", "label": "Use credit line", "impact": "+5.0"}
  ],
  "recommended_priority": ["suspend_tranches", "reduce_production_cost", "pause_advertising"]
}
```

### 1.3 新規：通知テンプレート生成

`financial_service.py` に `build_emergency_alert_templates(playbook)` を追加します。

Slack メッセージ例:

```text
🚨 Emergency Triggered: Cash Below Threshold
Current Cash: 16.9
Threshold: 18.0

Recommended Actions:
1. Suspend all pending tranches (+2.0)
2. Reduce production cost (+0.5)
3. Pause advertising (+0.3)

Run Playbook: /api/financials/execute-playbook
```

メールテンプレ例:

```text
Subject: [Alert] Emergency Liquidity Triggered

Cash has fallen below the threshold.

Current: 16.9
Threshold: 18.0

Recommended Actions:
- Suspend all pending tranches
- Reduce production cost
- Pause advertising

You can execute the playbook via:
POST /api/financials/execute-playbook
```

### 1.4 新規：通知サービス

新規ファイルを作成します。

- `src/backend/app/services/notification_service.py`

必須関数:

```python
def send_slack_alert(message: str) -> None:
    pass  # Webhook or API client


def send_email_alert(subject: str, body: str) -> None:
    pass  # SMTP or provider API
```

`financial_service.py` から呼び出しを追加します。

```python
if playbook_triggered:
    templates = build_emergency_alert_templates(playbook)
    notification_service.send_slack_alert(templates["slack"])
    notification_service.send_email_alert(
        templates["email_subject"],
        templates["email_body"]
    )
```

### 1.5 新規 API：プレイブック実行

`routes/financial.py` に新規エンドポイントを追加します。

- `POST /api/financials/execute-playbook`

機能:

- 実際のコスト削減や投資停止はログ記録のみ
- 将来の自動実行に備えて拡張可能な構造にする

Request:

```json
{
  "actions": ["suspend_tranches", "reduce_production_cost"]
}
```

Response:

```json
{
  "status": "executed",
  "executed_actions": ["suspend_tranches", "reduce_production_cost"],
  "timestamp": "2026-04-12T10:00:00Z"
}
```

---

## 2. ダッシュボード統合

### 2.1 対象ファイル

- `src/backend/app/services/executive_dashboard_service.py`
- `src/backend/app/models/executive_dashboard_model.py`

### 2.2 新規フィールド：Emergency Panel

`ExecutiveDashboard` に以下を追加します。

```json
"emergency_playbook": {
  "trigger": "...",
  "cash": 16.9,
  "threshold": 18.0,
  "actions": [...],
  "recommended_priority": [...]
}
```

### 2.3 UI 表示仕様（A-3 の続き）

Emergency Playbook Panel 表示例:

```text
🚨 Emergency Triggered: Cash Below Threshold
Cash: 16.9 / Threshold: 18.0

Recommended Actions:
✔ Suspend all pending tranches
✔ Reduce production cost
⚠ Pause advertising (optional)
💳 Use credit line (+5.0)

[Execute Playbook]
```

---

## 3. テスト仕様

### 3.1 新規テストファイル

- `tests/test_emergency_playbook.py`

### テスト項目

- プレイブック生成の正しさ
- 通知テンプレート生成
- Slack/メール送信関数の呼び出し
- `execute-playbook` API の動作
- ダッシュボードに `emergency_playbook` が含まれること

---

## 4. docs 追加内容

### 4.1 新規ドキュメント

- `/docs/emergency-playbook-overview.md`
- `/docs/emergency-playbook-api.md`
- `/docs/emergency-playbook-dashboard.md`

---

## 5. 実装順序（推奨）

1. バックエンド：通知サービス追加
2. `financial_service` に通知フック追加
3. `execute-playbook` API 実装
4. ダッシュボード統合
5. テスト追加
6. docs 追加

---

## 6. 完了条件（Definition of Done）

- 緊急プレイブックがキャッシュ閾値で自動生成される
- Slack/メール通知が送信される
- ダッシュボードに Emergency パネルが表示される
- プレイブック実行 API が動作する
- テストが全て通過する
- docs が更新されている
