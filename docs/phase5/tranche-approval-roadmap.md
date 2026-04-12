# Step A-1 → A-2 → A-3

## 部分承認トランシェ（Tranche Approval）機能：API ドキュメント・運用ルール・UI モック 指示書

---

## A-1. API ドキュメント（正式仕様）

### 1. 概要

部分承認トランシェ（Tranche Approval）は、投資リクエストを複数回に分割して承認・実行する仕組みです。
目的は、流動性リスクを抑えつつ成長投資を継続することです。

### 2. モデル仕様

#### InvestmentRequest（追加フィールド）

```jsonc
{
  "tranche_count": 3,               // 分割数（例：3回）
  "tranche_interval_months": 1      // トランシェ間隔（月）
}
```

#### InvestmentDecisionRecord（追加フィールド）

```jsonc
{
  "partial_candidate": 1.25,        // 部分承認候補額
  "tranche_schedule": [
    {"index": 1, "amount": 1.0, "scheduled_month": 202604},
    {"index": 2, "amount": 1.0, "scheduled_month": 202605},
    {"index": 3, "amount": 1.0, "scheduled_month": 202606}
  ],
  "tranche_index": 1                // 実行されたトランシェ番号
}
```

### 3. API 仕様

#### POST /api/financials/investment-request

投資リクエストを評価し、部分承認候補とトランシェスケジュールを返します。

##### Request

```json
{
  "id": "req-202604",
  "business_unit_id": "ai_solutions",
  "requested_amount": 3.0,
  "expected_return_rate": 0.18,
  "payback_period_months": 24,
  "strategic_priority": 4,
  "tranche_count": 3,
  "tranche_interval_months": 1
}
```

##### Response（例）

```json
{
  "investment_decision": {
    "decision": "Approved",
    "approved_amount": 3.0,
    "partial_candidate": 1.25,
    "tranche_schedule": [
      {"index": 1, "amount": 1.0, "scheduled_month": 202604},
      {"index": 2, "amount": 1.0, "scheduled_month": 202605},
      {"index": 3, "amount": 1.0, "scheduled_month": 202606}
    ]
  },
  "status": "pending"
}
```

> ※ `approved_amount` は、通常は `requested_amount` と一致しますが、部分承認候補が生成された場合は `tranche_schedule` の合計が `approved_amount` になります。

#### POST /api/financials/investment-decision

トランシェ実行を含む投資決定を適用します。

##### Request（例：第2トランシェ実行）

```json
{
  "investment_request_id": "req-202604",
  "decision": "Approved",
  "approved_amount": 1.0,
  "tranche_index": 2,
  "applied_month": 202605
}
```

##### Response（例）

```json
{
  "financials": {
    "cash_reserves": 16.0,
    "committed_capex": 3.0,
    "free_cash_flow": 1.9,
    ...
  },
  "decision": {
    "id": "dec-202604-2",
    "investment_request_id": "req-202604",
    "decision": "Approved",
    "approved_amount": 1.0,
    "tranche_index": 2,
    "applied_month": 202605,
    "reason": "第2トランシェを承認しました。",
    "impact_on_cash": -1.0
  }
}
```

#### GET /api/financials/emergency-playbook

緊急プレイブック（流動性逼迫時の推奨アクション）を返します。

##### Response（例）

```json
{
  "playbook": [
    {"priority": 1, "action": "新規投資を停止", "description": "流動性確保のため、すべての未決裁投資を一時停止します。", "status": "critical"},
    {"priority": 2, "action": "広告とマーケティングの出費削減", "description": "ROI が低い施策から停止し、即時のキャッシュ節約を図ります。", "status": "critical"},
    {"priority": 3, "action": "外注とサプライヤー支払いの見直し", "description": "支払い条件の交渉と優先順位付けを行い、キャッシュアウトを遅延させます。", "status": "critical"}
  ],
  "alert_templates": {
    "slack": "[緊急アラート] 現金残高が閾値を下回りました: 16.913. 即時対応が必要です。",
    "email": "経営チーム各位,\n\n現在のキャッシュ残高は 16.913 です。流動性閾値 18.000 を割り込んでいるため、以下の緊急プレイブックを確認してください。..."
  }
}
```

---

## A-2. 運用ルール（経営会議用）

### 1. トランシェ承認の目的

- ショック時のキャッシュ流出を平準化する
- 投資の実行力・効果を段階的に検証する
- 守りと攻めの両立を実現する

### 2. トランシェ承認の基本ルール

#### ✔ トランシェ数

- 原則 3 分割
- 例外的に 2〜4 分割を許可（要 CFO 承認）

#### ✔ トランシェ実行条件

各トランシェ実行前に以下を満たす必要があります。

- `cash_reserves >= minimum_cash_threshold + buffer`
- `buffer` の初期値：+3.0
- 市場ショックが解除されている、または影響が軽減している
- 組織実行力（execution capacity）がトランシェ額を上回る
- 前トランシェの成果が KPI で確認できる

### 3. 延期ルール

以下のいずれかに該当する場合、次トランシェは自動延期します。

- cash が閾値未達
- 市場インデックスが 0.9 未満
- 組織実行力が不足
- 前トランシェの KPI が未達成

#### 延期制限

- 延期は最大 3 回
- 3 回延期した場合は、残額は自動的に凍結されます

### 4. 緊急停止ルール

以下の条件で全トランシェ停止となります。

- `cash_reserves < minimum_cash_threshold`
- `emergency_playbook` が発動
- 市場ショックが 2 期以上継続
- 経営会議で停止決議

### 5. ダッシュボード表示ルール

表示すべき項目：

- 次トランシェ予定月
- 実行条件（達成 / 未達）
- KPI 達成状況
- 延期回数
- 緊急停止フラグ

---

## A-3. ダッシュボード UI モック（テキスト版）

以下は、実装チームに渡せる UI モックです。

### 📊 Investment Requests (Pending)

```
Request: req-202604 — AI Solutions Expansion
Requested: 3.0

Approved (Tranche): 1.0 / 1.0 / 1.0

Next Tranche: 2026/05

Tranche Conditions:

Cash ≥ 18.0 → ❌（現在 16.9）
Market Index ≥ 0.95 → ❌（0.87）
Execution Capacity ≥ 1.0 → ✔

Status: ⚠ 条件未達 → 自動延期（1/3）
```

### 🧭 Tranche Execution Timeline

| Tranche | Amount | Scheduled | Status | Notes |
|---------|--------|-----------|--------|-------|
| 1 | 1.0 | 2026/04 | ✔ Executed | KPI OK |
| 2 | 1.0 | 2026/05 | ⚠ Delayed | Cash below threshold |
| 3 | 1.0 | 2026/06 | Pending | — |

### 🚨 Emergency Playbook

```
Trigger: Cash < Threshold
Recommended Actions:

- Suspend all pending tranches
- Freeze new hiring (non-critical)
- Reduce external production cost (target: -0.5)
- Pause advertising for 1 month
- Consider credit line usage (+5.0 available)
```

### 📈 Financial Snapshot

```
Cash: 16.913
Free Cash Flow: 1.913
Committed Capex: 2.0
Market Shock: Stage Market -30% (active)
```

---

## 参考

- この指示書は `/docs/` 配下に置き、開発・経営両者が参照できる形式で管理してください。
- API 実装と並行して、運用ルールとダッシュボード表示を同時に整備することを推奨します。
