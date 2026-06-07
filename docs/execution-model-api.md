# Execution Capacity API

## エンドポイント

- `GET /api/execution/state`
  - 現在の実行力状態を返す
- `POST /api/execution/update`
  - 月次実績を反映して状態を更新する
- `GET /api/execution/forecast`
  - 次 3 ヶ月の実行力予測を返す

## リクエスト例

```json
{
  "month": 202604,
  "projects_completed": 3,
  "delays": 1,
  "kpi_success_rate": 0.75,
  "capacity": 12.0,
  "load": 4.0
}
```

## レスポンス例

```json
{
  "capacity": 12.0,
  "load": 4.0,
  "efficiency": 0.82,
  "execution_capacity_score": 6.56,
  "history": [ ... ]
}
```
