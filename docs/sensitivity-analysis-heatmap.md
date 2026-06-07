# Sensitivity Analysis Heatmap

## 目的

感度分析の結果から、`max_investment_pct_of_cash` と `minimum_cash_threshold` の組み合わせを可視化します。

## 実行方法

1. `run_sensitivity_batch.py` を実行して `sensitivity_outputs/` を生成します。
2. `generate_sensitivity_comparison.py` を実行して CSV を生成します。
3. `plot_sensitivity_heatmap.py` を実行して PNG を生成します。

```bash
python generate_sensitivity_comparison.py
python plot_sensitivity_heatmap.py
```

## 出力

- `sensitivity_outputs/comparison_sensitivity_<timestamp>.csv`
- `sensitivity_outputs/sensitivity_heatmap_<metric>_<timestamp>.png`

## 注意

- `matplotlib` がインストールされていない場合、PNG 生成はスキップされます。
- 必要に応じて `plot_sensitivity_heatmap.py` を拡張し、`shock_strength` / `shock_duration` のスライスを指定できます。
