# Emergency Playbook Overview

## 目的

Emergency Playbook は、キャッシュ閾値を割り込んだときに即応するための推奨アクションセットです。
Downside や Simultaneous シナリオでのリスクを低減し、経営判断のスピードを確保するために設計されました。

## 機能

- 緊急トリガー検出
- 推奨アクションの生成
- 通知テンプレートの生成 (Slack / Email)
- プレイブック実行 API
- ダッシュボードへの Emergency パネル統合

## 主なトリガー

- `cash_below_threshold`
- `cash_below_buffer`
- `stable`

## 出力項目

- trigger
- cash
- threshold
- status
- actions
- recommended_priority
