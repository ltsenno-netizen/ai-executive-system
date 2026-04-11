# AI Executive System API Workflows

## 月次運営ワークフロー

1. `GET /api/company/monthly-pl`
2. `POST /api/company/simulate-month-full`
3. 必要に応じて `POST /api/company/simulate-month` を使い、単月 PL の詳細を確認

## 改善ループワークフロー

1. `POST /api/improvement/simulate-cycle`
2. `GET /api/improvement/history`
3. `GET /api/improvement/priority`

## Executive Dashboard ワークフロー

1. `GET /api/executive/dashboard?month={month}`
2. `GET /api/executive/forecast?month={month}`
3. `GET /api/executive/month/{month}`

## 課題検知／改善施策ワークフロー

1. `POST /api/issues/detect`
2. `POST /api/issues/recommend`
3. `POST /api/issues/simulate-month`

## 戦略ワークフロー

1. `GET /api/strategy/midterm`
2. `POST /api/strategy/gap-analysis`
3. `POST /api/strategy/recommend`
4. `POST /api/strategy/simulate-year`

## 実行例

- 会社の月次状況を把握するには: `GET /api/company/monthly-pl`
- 課題と改善施策を確認するには: `POST /api/issues/detect` → `POST /api/issues/recommend`
- 経営ダッシュボードを確認するには: `GET /api/executive/dashboard?month=7`
