# Meta-Cognition Overview

## 1. 目的

Meta-Cognition Layer は、企業の「自己評価 OS」です。意思決定プロセスを評価し、各レイヤーの影響度を数値化し、偏りや過剰依存を検知し、改善アクションを提案します。

## 2. 対象レイヤー

- Intent（AA）
- Executive Agents（AB）
- Autonomous Loop（AC）
- Frontier Optimization（AD）
- Consciousness（AE）
- Consciousness Evolution（AF）
- Narrative Intelligence（AG）
- Corporate Memory（AH）

## 3. モデル層

`src/backend/app/models/meta_cognition_model.py` には以下を実装します。

- `MetaDimension`: 評価対象の 8 次元
- `MetaScore`: 各次元のスコア、信頼度、根拠
- `MetaBias`: 検出されたバイアス、深刻度、影響領域
- `MetaCognitionReport`: 総合スコア、各次元スコア、バイアス、推奨アクション、タイムスタンプ

## 4. エンジン層

`src/backend/app/services/meta_cognition_engine.py` では、各次元を評価する関数を実装します。

- `evaluate_intent`
- `evaluate_agents`
- `evaluate_autonomous`
- `evaluate_frontier`
- `evaluate_consciousness`
- `evaluate_evolution`
- `evaluate_narrative`
- `evaluate_memory`

`detect_biases` は次のようなパターンを検出します。

- AGENTS 高・INTENT 低 → 「現場ドリブン過多」
- NARRATIVE 高・FRONTIER 低 → 「語り先行」
- MEMORY 偏り → 「成功バイアス」
- AUTONOMOUS 高・FRONTIER 低 → 「過度な自動化依存」

`build_meta_cognition_report` は全次元のスコアを統合し、レポートを生成します。

## 5. サービス層

`src/backend/app/services/meta_cognition_service.py` は各サービスから最新状態を取得し、レポート生成を実行します。

- `run_assessment`: 状態を収集し、レポートを生成、JSON に保存、必要なら Corporate Memory に記録
- `get_latest`: 最新レポートを返す
- `get_history`: レポート履歴を返す
- `export_report_markdown`: Markdown 表示用に出力

## 6. REST API

`src/backend/app/routes/meta_cognition.py` で以下のエンドポイントを提供します。

- `POST /api/meta-cognition/run`
- `GET /api/meta-cognition/latest`
- `GET /api/meta-cognition/history`
- `GET /api/meta-cognition/markdown/{report_id}`

## 7. ダッシュボード統合

ダッシュボードに `MetaCognitionSummary` を追加し、最新レポートを集約します。

- `overall_score`
- `top_risks`
- `strongest_dimensions`
- `weakest_dimensions`
- `last_assessed`

## 8. テスト

- `tests/test_meta_cognition_engine.py`
- `tests/test_meta_cognition_service.py`
- `tests/test_meta_cognition_api.py`
- `tests/test_dashboard_meta_cognition_summary.py`

それぞれのテストは評価ロジック、サービスの履歴、API エンドポイント、ダッシュボード統合を検証します。
