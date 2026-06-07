# Emergency Playbook Dashboard

## Emergency Playbook Panel

```
🚨 Emergency Triggered: Cash Below Threshold
Cash: 16.9 / Threshold: 18.0

Recommended Actions:
✔ Suspend all pending tranches
✔ Reduce production cost
⚠ Pause advertising (optional)
💳 Use credit line (+5.0)

[Execute Playbook]
```

## Financial Snapshot

- Cash: 16.913
- Free Cash Flow: 1.913
- Committed Capex: 2.0
- Market Shock: Stage Market -30% (active)

## 状態別 UI

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
