# AI CEO Succession Overview

## 目的
AI CEO が継続的に学習を進めると、経営スタイルが極端に偏ったり、リスク管理に課題が出たりします。
本機能は次のフェーズを支援します。

- 現CEOの学習履歴から後継候補（Next-Gen CEO）を生成
- Boardが候補を評価して後継CEOを選任
- CEO交代イベントを発生させる
- 新CEOが前任者のスタイルを引き継ぎつつ変化させる
- 交代後の経営影響をダッシュボードで可視化する

## 後継者生成ロジック

`src/backend/app/services/ceo_succession_engine.py` では、現CEOの `AICeoPersona` をベースに3名の候補を生成します。

- Candidate A（継承型）: 現CEOに近く、リスク許容度はやや低め
- Candidate B（攻め型）: `aggressiveness +0.1`, `brand_priority +0.1`
- Candidate C（守り型）: `risk_tolerance -0.1`, `short_term_focus -0.1`

各候補には強み・弱み・現CEOとの類似度・革新偏向度が付与されます。

## Board による選任プロセス

`src/backend/app/services/ai_board_agent.py` を拡張し、候補者ごとの投票ロジックを実装しました。

- Financial Director: 財務健全性とキャッシュ圧迫を重視
- Brand Director: ブランド優先度と長期視点を重視
- Risk Director: 低リスク候補を支持
- Org Director: 短期実行負荷を重視

最多得票者を選任し、同票の場合は `Risk Director` の投票を優先します。

## CEO Succession Service

`src/backend/app/services/ceo_succession_service.py` では次を実装しています。

1. 現CEOの `AICeoPersona` を取得
2. 直近6ヶ月の学習履歴を取得
3. 候補者を生成
4. Boardによる候補者選任
5. 新CEO personaを保存
6. `CeoSuccessionDecision` を保存

後継者決定は `data/ceo_succession/<period>.json` に記録されます。

## 交代イベント発生タイミング

`src/backend/app/services/monthly_batch_service.py` にSuccession判定を追加しました。
以下の条件で発火します。

- 任期満了（例：3年周期の12月）
- 財務悪化（営業利益マイナス、現金残高1.0未満）
- CEO personaが極端に偏っている場合
- Boardが問題視した場合（meeting_stateで `rejected` / `conditional` を検出）
- 組織負荷が高い場合

該当時には `CeoSuccessionService.run_ceo_succession()` を呼び出します。

## ダッシュボード統合

`src/backend/app/models/executive_dashboard_model.py` に `CeoSuccessionSummary` を追加し、
`src/backend/app/services/executive_dashboard_service.py` で最新の後継者選定履歴を集約します。

ダッシュボードには、最新の交代期と新CEO persona、選任理由が含まれます。

## API

- `POST /api/ceo-succession`
  - 期間を指定し、後継者選任を実行
- `GET /api/ceo-succession/latest`
  - 最新のSuccessionDecisionを取得

## 追加テスト

- 候補者生成ロジック
- Boardによる候補者選択
- サービスの実行と保存
- ダッシュボードへの反映
