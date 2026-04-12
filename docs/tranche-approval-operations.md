# Tranche Approval Operations

## 1. 目的と背景

部分承認トランシェは、投資リクエストを複数回に分割して承認・実行する仕組みです。
目的は、流動性リスクを抑えつつ成長投資を継続し、投資の実行効果を段階的に検証することです。

特に Downside シナリオでは、1 回の大型投資よりもトランシェ分割によるキャッシュ平準化が有効です。

## 2. 承認フロー図

```
Investment Request
      ↓
Financial Evaluation
      ↓
Tranche Schedule Generation
      ↓
Condition Check (cash, market, execution)
      ├─ OK → Execute Tranche
      ├─ NG → Delay (max 3)
      └─ Emergency → Stop All
```

## 3. トランシェ実行条件

以下の数値基準を満たす必要があります。

| 条件 | 基準値 | 説明 |
|------|--------|------|
| Cash buffer | `minimum_cash_threshold + 3.0` | 次トランシェ実行前の流動性バッファ |
| Market index | `>= 0.95` | 市場環境が回復傾向にあること |
| Execution capacity | `>= tranche_amount` | 組織が実行可能な負荷であること |
| KPI | 前トランシェの KPI 達成 | 投資効果が確認できること |

### 初期パラメータ

- `buffer` 初期値: `3.0`
- `tranche_count` 原則: `3`
- `tranche_interval_months` 原則: `1`

## 4. 延期ルール

以下のいずれかが発生した場合、次トランシェは自動延期されます。

- cash が閾値未達
- market index が `0.9` 未満
- execution capacity が不足
- 前トランシェの KPI 未達成

### 延期条件

- 延期は最大 3 回まで
- 3 回延期した場合、残額は自動的に凍結されます

## 5. 緊急停止ルール

以下の条件で全トランシェを停止します。

- `cash_reserves < minimum_cash_threshold`
- `emergency_playbook` が発動
- 市場ショックが 2 期以上継続
- 経営会議で停止決議

## 6. 例外規定（CEO/CFO 承認）

以下の場合に例外承認を許可します。

- CEO/CFO が承認した場合のみ、`tranche_count` を 2〜4 に変更可能
- `priority >= 5` の戦略案件は 1 回だけ特例実行可能
- ショック期間中は原則停止とするが、中長期戦略案件は別途経営判断とする

## 7. ダッシュボード表示ルール

表示項目:

- 次トランシェ予定日
- 条件達成状況（✔ / ⚠ / ❌）
- 延期回数
- 緊急停止フラグ
- KPI 達成状況（色分け）

## 8. KPI 要件

前トランシェの成果を確認し、次トランシェ実行の判断材料とします。

- 達成基準は投資案件ごとに設定
- KPI は売上、利益率、リード獲得、進捗指標などを含む
- KPI 未達の場合、次トランシェは原則延期または再評価とする

## 9. 運用例: 2026/4 Downside ケース

- 2026/04: 第 1 トランシェ 1.0 を実行
- Cash: `16.913`（`minimum_cash_threshold + buffer` を下回る）
- Market Shock: `Stage Market -30%` が継続
- 結果: 第 2 トランシェは条件未達で延期
- 代替措置: `Emergency Playbook` を起動し、コスト削減と与信枠の検討を行う

この運用例では、トランシェ分割により流動性リスクを抑えつつ、次フェーズの実行判断を保留できることを示します。