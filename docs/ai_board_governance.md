# AI Board Governance Layer

## 1. 目的

AI Board Governance Layer は、AI CEO の意思決定に対して多様な取締役会視点のレビューと承認プロセスを追加する機能です。これにより、AI経営判断の信頼性とリスク管理が強化されます。

## 2. 役割

- **AI CEO**: 既存の意思決定エンジンとして、戦略的な選択肢の提示と方針決定を行う。
- **AI Board**: 複数の専門取締役（財務・ブランド・リスク・組織）から構成される取締役会。AI CEO の選択を多角的にレビューし、合議制で承認・条件付き承認・差し戻しを判断する。

## 3. 取締役構成

- **Financial Director**: 財務健全性とキャッシュフロー管理を重視
- **Brand Director**: ブランド価値と長期的な市場ポジションを重視
- **Risk Director**: リスク評価とダウンサイド保護を重視
- **Org Director**: 組織キャパシティと実行可能性を重視

## 4. 判断ロジック

AI Board は以下の条件をもとに合議制で評価します。

- **リスクフラグの集約**: 各取締役のリスク指摘（risk_flag）を集計
  - 2つ以上のリスクフラグ: 差し戻し（rejected）
  - 1つのリスクフラグ: 条件付き承認（conditional）
- **支持度の評価**: CEO案への支持度を評価
  - 75%以上の支持: 承認（approved）
  - それ以外: 条件付き承認（conditional）または多数決による代替案採用
- **最終決定**: リスクフラグと支持度を総合的に判断し、最適な決定案を選択

## 5. 出力

- `status`: `approved` / `conditional` / `rejected`
- `final_option_id`: 最終判断案のID
- `final_option_label`: 最終判断案のラベル
- `board_rationale`: 取締役会の判断理由
- `conditions`: 条件付き承認・差し戻し時の執行条件
- `member_opinions`: 各取締役の個別意見（role, preferred_option_id, rationale, risk_flag）

## 6. システム反映

- 月次レポート: 取締役会の判断セクションを追加し、最終決定案と各取締役の意見を明示。
- Executive Dashboard: 会議サマリーに取締役会評価を含め、意思決定のガバナンス状況を可視化。
- Narrative Engine: 取締役会の合議プロセスと多様な視点の議論を物語風に表現。
- 会議状態: `AI CEO + Board` を最終決定者として保存し、ボード評価の結果を `board_decision` として永続化する。

## 7. ダッシュボード上の Board 表示仕様

### フィールド一覧

- `board_status`: 取締役会の判断結果。`approved` / `conditional` / `rejected`。
- `board_final_option_label`: 取締役会が最終的に承認した決定案のラベル。
- `board_rationale`: 取締役会の判断理由。
- `board_conditions`: 条件付き承認・差し戻し時の執行条件。
- `board_member_opinions`: 各取締役の個別意見リスト。

### 表示イメージ

```
meeting:
  selected_option_label: "バランス型"
  board_status: "conditional"
  board_final_option_label: "守り寄り成長案"
  board_member_opinions:
    - role: "financial"
      preferred_option_id: "B"
      rationale: "キャッシュ残高が不足するリスクあり"
      risk_flag: true
    - role: "brand"
      preferred_option_id: "A"
      rationale: "ブランド価値向上の機会"
      risk_flag: false
```
  board_rationale: "キャッシュ水準と中期ブランド価値の両立を優先したため。"
  board_conditions: "来期も同様の投資を行う場合は、キャッシュ残高を再評価すること。"
```

この表示により、「CEO はこう言ったけど、Board はこう判断した」が一目で追えるようになります。
