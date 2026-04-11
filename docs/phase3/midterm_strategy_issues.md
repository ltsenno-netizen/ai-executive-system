# Phase 3：中期戦略モデル GitHub Issues

## Issue: 中期戦略モデルの実装
- 目的: 中期戦略テーマ、年度目標、戦略施策をデータモデルとして定義する。
- 参照: `src/backend/app/models/midterm_strategy_model.py`, `data/samples/midterm_strategy_model.json`

## Issue: KPIギャップ分析ロジックの実装
- 目的: 現状の KPI と戦略目標の差分を評価し、`StrategyGap` を生成する。
- 参照: `src/backend/app/services/midterm_strategy_service.py`

## Issue: 戦略施策提案ロジックの実装
- 目的: ギャップが大きいテーマに紐づく施策を優先的に提案する。
- 参照: `src/backend/app/services/midterm_strategy_service.py`

## Issue: 年間戦略シミュレーションAPIの実装
- 目的: `POST /api/strategy/simulate-year` を実装し、年間 KPI 集計とギャップ分析を返す。
- 参照: `src/backend/app/routes/midterm_strategy.py`

## Issue: E2Eテスト（1年シミュレーション＋ギャップ分析）
- 目的: 12ヶ月の統合シミュレーションを通じて、戦略レイヤーの整合性を検証する。
- 参照: `tests/test_midterm_strategy.py`
