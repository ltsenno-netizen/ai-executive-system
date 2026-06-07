# Executive Simulation Overview

Step AN: Executive Simulation Engine は、AI 役員ロールが共通のインプットを見て議論し、合意戦略案とコンセンサスを出力するためのシミュレーション層です。

## コンポーネント

- `src/backend/app/models/executive_simulation_model.py`
  - `ExecutiveRole`, `ExecutiveStance`
  - `ExecutiveComment`, `ExecutiveVote`
  - `ExecutiveSimulationInput`, `ExecutiveSimulationResult`
  - `StrategyBundle`

- `src/backend/app/services/executive_simulation_engine.py`
  - `generate_comment_for_role`
  - `decide_stance_for_role`
  - `compute_consensus_level`
  - `build_ceo_summary`
  - `ExecutiveSimulationEngine.run_executive_simulation`

- `src/backend/app/services/executive_simulation_service.py`
  - 入力シナリオの取得・戦略バンドルの生成または再利用
  - 比較報告・メタ認知報告の取得
  - シミュレーション結果の永続化
  - Corporate Memory への履歴保存

- `src/backend/app/services/executive_simulation_repository.py`
  - `data/executive_simulation/history.json` に保存

- `src/backend/app/routes/executive_simulation.py`
  - `POST /api/executive-simulation/run`
  - `GET /api/executive-simulation/latest`
  - `GET /api/executive-simulation/history`
  - `GET /api/executive-simulation/{simulation_id}`
  - `GET /api/executive-simulation/{simulation_id}/markdown`

- ダッシュボード統合
  - `ExecutiveSimulationSummary` をダッシュボードに追加
  - `ExecutiveDashboardService._aggregate_executive_simulation_summary`

## 特徴

- ロールベースのコメント生成は軽量ルールベースで実装
- スタンスはリスク・機会・提案の数に基づき決定
- コンセンサスは投票スタンスの平均化によって算出
- CEO サマリーには懸念・修正提案・最終判断を含む
