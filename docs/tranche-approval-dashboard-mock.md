# Tranche Approval Dashboard Mock

## Pending Investment Requests パネル

### 例: req-202604 — AI Solutions Expansion

- Requested: `3.0`
- Approved (Tranche): `1.0 / 1.0 / 1.0`
- Next Tranche: `2026/05`
- Delay Count: `1 / 3`

### Condition Check

```
[Next Tranche: 2026/05]
Condition Check:
  Cash: ❌ (16.9 < 18.0)
  Market Index: ❌ (0.87 < 0.95)
  Execution Capacity: ✔
  KPI: ✔
Status: ⚠ Delayed (1/3)
```

## Tranche Execution Timeline

| Tranche | Amount | Scheduled | Status | Notes |
|--------|--------|-----------|--------|-------|
| 1 | 1.0 | 2026/04 | ✔ Executed | KPI OK |
| 2 | 1.0 | 2026/05 | ⚠ Delayed | Cash below threshold |
| 3 | 1.0 | 2026/06 | Pending | — |

## Emergency Playbook パネル

```
🚨 Emergency Playbook Activated
Reason: Cash < Threshold

Recommended Actions:
1. Suspend pending tranches
2. Freeze non-critical hiring
3. Reduce production cost (-0.5)
4. Pause advertising (1 month)
5. Consider credit line usage (+5.0)

[Execute Playbook] [Dismiss]
```

## Financial Snapshot

- Cash: `16.913`
- Free Cash Flow: `1.913`
- Committed Capex: `2.0`
- Market Shock: `Stage Market -30% (active)`

## 状態別 UI バリエーション

### 条件達成

```
[Next Tranche: 2026/05]
Condition Check:
  Cash: ✔ (20.0 >= 18.0)
  Market Index: ✔ (0.98 >= 0.95)
  Execution Capacity: ✔
  KPI: ✔
Status: ✔ Ready to execute tranche
```

### 条件未達

```
[Next Tranche: 2026/05]
Condition Check:
  Cash: ❌ (16.9 < 18.0)
  Market Index: ⚠ (0.92 < 0.95)
  Execution Capacity: ✔
  KPI: ✔
Status: ⚠ Delayed (1/3)
```

### 緊急停止

```
[Next Tranche: 2026/05]
Condition Check:
  Cash: ❌ (14.0 < 18.0)
  Market Index: ❌ (0.80 < 0.95)
  Execution Capacity: ❌
  KPI: ❌
Status: 🚨 Emergency stop - all tranches suspended
```

### KPI 未達

```
[Next Tranche: 2026/05]
Condition Check:
  Cash: ✔ (19.0 >= 18.0)
  Market Index: ✔ (0.96 >= 0.95)
  Execution Capacity: ✔
  KPI: ❌
Status: ⚠ Delayed due to KPI performance
```

## Tranche History

```
Tranche History:
- 2026/04: Executed (1.0) ✔ KPI OK
- 2026/05: Delayed (cash below threshold)
- 2026/06: Pending
```

## UI モックの用途

- 実装チームはこの Markdown を参照し、ダッシュボードの表示レイアウトと状態別表現を実装してください。
- Emergency Playbook はステータス表示と実行ボタンを持ち、実行アクションはログ記録として扱います。}}