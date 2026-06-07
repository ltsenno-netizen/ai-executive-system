# Monthly Batch Overview

## 目的

1ヶ月分の経営サイクルをバッチとして一括実行し、シミュレーションからレポート生成までを自動化します。

将来的には複数月連続実行や定期実行（cron）への拡張を想定します。

## フロー

run_monthly_cycle(period)
  ├─ run_monthly_simulation(period)
  ├─ run_executive_meeting(period)
  ├─ apply_meeting_decision(period)
  ├─ generate_narrative(period)
  ├─ generate_report(period)
  └─ update_dashboard_state(period)

## 新規コンポーネント

### monthly_batch_service.py

- `MonthlyBatchResult`
- `run_monthly_cycle(period: str) -> MonthlyBatchResult`
- `run_multi_month_cycle(start_period: str, months: int) -> List[MonthlyBatchResult]`

### MonthlyBatchResult

```python
class MonthlyBatchResult(BaseModel):
    period: str
    simulation_ok: bool = False
    meeting_ok: bool = False
    narrative_ok: bool = False
    report_ok: bool = False
    errors: List[str] = []
```

## 既存サービス連携ポイント

- `CompanyOperationsIntegrationService.simulate_month_full()`
- `ExecutiveMeetingService.build_meeting_agenda()`
- `ExecutiveMeetingService.generate_decision_options()`
- `ExecutiveMeetingService.apply_decision_option()`
- `ExecutiveNarrativeService.generate_and_store_narrative()`
- `ExecutiveReportService.generate_and_store_report()`
- `ExecutiveDashboardService.build_dashboard()`

## API 仕様

### POST /api/batch/monthly

リクエスト:

```json
{ "period": "2026-04" }
```

レスポンス:

```json
{
  "period": "2026-04",
  "simulation_ok": true,
  "meeting_ok": true,
  "narrative_ok": true,
  "report_ok": true,
  "errors": []
}
```

## 拡張候補

- `run_multi_month_cycle(start_period, months)` で連続月実行
- cron 連携で定期実行
- エラー発生時の再試行ロジック
- 失敗ステージの詳細ログ

## テスト要件

- 成功系: 全ステップ成功でフラグがすべて `True`
- 異常系: 例外発生時に `errors` が記録され、途中までのフラグのみ `True`

## 完了条件

- `run_monthly_cycle("2026-04")` でシミュレーション、会議、Narrative、Report が順に実行される
- エラー時に `MonthlyBatchResult` に記録される
- テストが通過する
- ドキュメントが更新されている
