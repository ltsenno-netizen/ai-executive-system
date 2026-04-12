# Pull Request Template

## PR タイトル

`Step A: Tranche Approval — API Docs, Operations Guide, Dashboard Mock`

## 概要

この PR では、トランシェ承認（Tranche Approval）機能の運用化に向けたドキュメントを追加します。

## 追加ファイル

- `docs/financials_tranche_approval.yaml`
- `docs/tranche-approval-operations.md`
- `docs/tranche-approval-dashboard-mock.md`

## 目的

- 部分承認トランシェの API 仕様を明確化
- 経営会議で使える運用ルールを整備
- ダッシュボード実装のための UI モックを提供

## 変更点

- `API`:
  - `/financials/investment-request`
  - `/financials/investment-decision`
  - `/financials/emergency-playbook`
- `運用ルール`:
  - 承認フロー
  - トランシェ実行条件
  - 延期/停止ルール
  - 例外規定
- `UI モック`:
  - Pending request パネル
  - Tranche timeline
  - Emergency playbook panel
  - 状態別表示例

## テスト

- ドキュメントの GitHub Markdown 表示確認
- OpenAPI YAML の 3.1 構文チェック

## 今後の予定

- フロント統合
- Emergency Playbook の UI 実装
- Slack / メール通知フック
- 感度分析バッチ
- 実行力モデルの統合

## 備考

必要であれば、追加の PR テンプレートやレビューガイドを作成できます。