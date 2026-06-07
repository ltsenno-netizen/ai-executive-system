# Execution Capacity Model Overview

## 目的

実行力モデルは、投資判断が「お金」だけでなく「実行力」に依存することを評価します。実行力を定量化し、投資承認とトランシェ実行の整合性を高めます。

## モデル要素

- Capacity: 月間で処理できるプロジェクト量
- Load: 現在進行中のプロジェクト負荷
- Efficiency: 過去実績に基づく実行効率

### 実行力スコア

```text
execution_capacity_score = (capacity - load) * efficiency
```

## データ構造

- `ExecutionState`
- `ExecutionRequirement`
