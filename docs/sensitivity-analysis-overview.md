# Sensitivity Analysis Overview

このドキュメントは、投資ポリシーと市場ショックを変化させた 24 ヶ月シミュレーションの感度分析バッチの目的と設計を説明します。

## 目的

- 投資ポリシーを変化させることで「攻めすぎ」「守りすぎ」のバイアスを検証する
- 市場ショックの影響を組み合わせて、最適な経営ポリシーを定量的に探索する
- 51〜100 シナリオの小規模セットでテストを進め、最終的に 480 シナリオのフル実行を目指す

## 主要指標

- final_cash
- min_cash
- avg_fcf
- approvals
- rejections
- tranche_delays

## 生成する成果物

- `sensitivity_outputs/scenario_<params>_monthly.csv`
- `sensitivity_outputs/scenario_<params>_summary.json`
- `sensitivity_outputs/comparison_sensitivity_<timestamp>.csv`
- `sensitivity_outputs/sensitivity_heatmap_<metric>_<timestamp>.png` (matplotlib がインストールされている場合)
