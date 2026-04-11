# Phase 9: Corporate Fundamentals Model

## 概要

Phase 9 では、企業ファンダメンタルズモデルを導入し、仮想企業のアイデンティティ、財務基盤、事業構造、顧客セグメント、組織体制、会社の歴史的背景を表現します。

### 目的

- 企業戦略と意思決定の基盤として「会社らしさ」を持たせる
- 事業別の費用・収益構造に企業固有の制約を反映する
- 財務と KPI に企業の資本構成・コスト構造情報を流し込む
- 会社の過去の意思決定と文化が課題/戦略に与える影響を表現する

## モデル構成

- `profile`: 企業プロフィール、ビジョン、ミッション、経営スタイル
- `business_units`: 事業ごとの売上モデル、費用構造、KPI ドライバ
- `customer_segments`: 顧客ごとの行動パターン、価格感度
- `organization_units`: 部門の役割、スキル、文化特性
- `financials`: 固定費、変動費、資産、負債、キャッシュリザーブ、財務指標
- `history`: 会社の重要イベントとそれが戦略・組織に与えた影響

## API エンドポイント

- `GET /api/fundamentals` - 企業ファンダメンタルズ全体モデルを返す
- `GET /api/fundamentals/history` - 会社の歴史イベント一覧を返す
- `GET /api/fundamentals/impact?month=7&year=2026` - 指定月の PL/KPI に企業ファンダメンタルズを反映した影響を返す

## インテグレーション

- `CompanyOperationsIntegrationService` に CorporateFundamentalsService を導入し、月次シミュレーション結果に企業固有の固定費や事業別コスト構造を反映
- External Environment の影響を受けた収益・KPI 計算の後に、企業ファンダメンタルズを上書き適用
- ダッシュボードおよび課題検出ロジックにファンダメンタルズの結果を活用するための拡張ポイントを確保

## テスト

- `tests/test_corporate_fundamentals.py` に以下を実装
  - モデル読み込みテスト
  - 月次影響計算テスト
  - API エンドポイントのレスポンス構造テスト

## 今後の拡張

- `history.impact_on_strategy` を戦略生成ロジックに直接反映
- `financials.financial_health_indicators` をダッシュボードスコアリングに活用
- 事業別 `linked_market_segments` を外部環境セグメントと紐づける
