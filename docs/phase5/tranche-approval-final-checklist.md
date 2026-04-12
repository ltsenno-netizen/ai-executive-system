# tranche-approval-roadmap.md 仕上げ指示書

この指示書は、既に作成済みの `tranche-approval-roadmap.md` を正式な GitHub ドキュメントとして完成させるための最終作業内容をまとめたものです。

## ✅ A-1 API ドキュメント仕上げ指示

### 1. OpenAPI 仕様の追加（任意だが推奨）
以下を含む YAML を作成し、`/docs/api/financials_tranche.yaml` に配置します。

- `/api/financials/investment-request`
  - request body schema
  - response schema（`partial_candidate`, `tranche_schedule` を含む）
- `/api/financials/investment-decision`
  - `tranche_index` の説明
- `/api/financials/emergency-playbook`
  - `emergency_playbook` の構造

目的：
外部ツール（Stoplight, SwaggerHub）で可視化できるようにする。

### 2. Markdown ドキュメントに追記すべき内容
`tranche-approval-roadmap.md` に以下を追加します。

- API エンドポイント一覧表
- フィールド定義表（型・説明・例）
- トランシェスケジュールの JSON 例
- エラーケース（条件未達・延期・停止）
- HTTP ステータスコード一覧

### 3. サンプルリクエスト/レスポンスの追加
最低 3 種類を掲載します。

- Full approval
- Partial candidate only（Deferred）
- Tranche approval（3 分割）

---

## ✅ A-2 運用ルール仕上げ指示

### 1. 経営会議向けの「承認フロー図」を追加
Markdown で以下を追記します。

```text
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

### 2. トランシェ実行条件の “数値基準” を明文化
例を含めて明確に記述します。

| 条件 | 基準値 | 説明 |
|------|--------|------|
| Cash buffer | `minimum_cash_threshold + 3.0` | 流動性確保 |
| Market index | `>= 0.95` | 市場回復確認 |
| Execution capacity | `>= tranche_amount` | 実行可能性 |
| KPI | 前トランシェの KPI 達成 | 効果検証 |

### 3. 延期・停止ルールの「例外規定」を追加

a. 例外承認（CEO/CFO）

b. 戦略案件（`priority >= 5`）は 1 回だけ特例実行可能

c. ショック期間中は原則停止

### 4. ダッシュボード表示ルールの詳細化
以下の表示要件を明記します。

- 次トランシェ予定日
- 条件達成状況（✔ / ⚠ / ❌）
- 延期回数
- 緊急停止フラグ
- KPI 達成状況（色分け）

---

## ✅ A-3 UI モック仕上げ指示

### 1. ダッシュボード構成を Markdown で明確化
以下の 3 つのパネルを定義します。

- Pending Investment Requests
- Tranche Execution Timeline
- Emergency Playbook Panel

### 2. UI モックの “状態別バリエーション” を追加
下記の状態について、例を追加します。

- 条件達成 → 実行可能
- 条件未達 → 延期
- 緊急停止 → 全停止
- KPI 未達 → 警告

例：

```text
[Next Tranche: 2026/05]
Condition Check:
  Cash: ❌ (16.9 < 18.0)
  Market Index: ❌ (0.87 < 0.95)
  Execution Capacity: ✔
  KPI: ✔
Status: ⚠ Delayed (1/3)
```

### 3. Emergency Playbook の UI モックを追加
以下のブロックを追加します。

```text
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

### 4. トランシェ実行履歴の UI モック
以下を追加します。

```text
Tranche History:
- 2026/04: Executed (1.0) ✔ KPI OK
- 2026/05: Delayed (cash below threshold)
- 2026/06: Pending
```

---

## 📌 最終チェックリスト（docs に入れる前に）

### API
- [ ] OpenAPI YAML を追加
- [ ] サンプル JSON を 3 種類掲載
- [ ] エラーケースを明記

### 運用ルール
- [ ] フロー図
- [ ] 数値基準
- [ ] 例外規定
- [ ] ダッシュボード表示ルール

### UI モック
- [ ] 状態別 UI
- [ ] Emergency Playbook
- [ ] Tranche Timeline
- [ ] KPI 表示
