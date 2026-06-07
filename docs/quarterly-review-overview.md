# 四半期レビュー（Quarterly Review）概要

## 目的

月次の積み上げを「四半期単位」で総括し、中期計画（MTP）とのギャップ分析 → Board レビュー → 次四半期の重点テーマ設定までを自動化する。これにより、企業の経営サイクルが以下のように完成する：

```
月次 → 四半期 → 中期 → ガバナンス → 学習 → 次期計画
```

## MTP との関係

- **入力**: 中期計画の四半期目標（売上・利益目標）
- **分析**: 実際の四半期実績 vs MTP目標 のギャップ分析
- **出力**: 次四半期の重点テーマ（MTP達成に向けた是正施策）

## Board レビューの位置づけ

- **レビュー対象**: 四半期実績の総括と次四半期計画
- **合議制**: 財務・ブランド・リスク・組織の各取締役が評価
- **判定**: 承認 / 条件付き承認 / 差し戻し
- **影響**: 次四半期の重点テーマに Board の意見を反映

## システム構成

### モデル（quarterly_review_model.py）

```python
class QuarterlyReview(BaseModel):
    quarter: str  # "2026-Q1"
    financial: QuarterlyFinancialSummary
    execution: QuarterlyExecutionSummary
    gap_analysis: str
    next_quarter_focus: List[str]
    board_review: QuarterlyBoardReview
```

### エンジン（quarterly_review_engine.py）

- **build_quarterly_review()**: 四半期レビューの生成メイン関数
- **_build_financial_summary()**: 3ヶ月分の財務データ集計
- **_build_execution_summary()**: 施策完了/遅延、組織負荷の集計
- **_build_gap_analysis()**: MTPとのギャップ分析
- **_generate_next_quarter_focus()**: 次四半期重点テーマ生成
- **_conduct_board_review()**: Board合議制レビュー

### サービス（quarterly_review_service.py）

- **generate_quarterly_review()**: 四半期レビュー生成・保存
- **get_quarterly_review()**: 特定四半期レビューの取得
- **get_latest_quarterly_review()**: 最新レビューの取得
- **_save_review()**: JSON/Markdown形式での保存

## ダッシュボード表示例

```json
{
  "quarterly_review": {
    "quarter": "2026-Q1",
    "revenue_total": 3200000,
    "profit_total": 410000,
    "board_status": "conditional",
    "next_quarter_focus": [
      "制作費の最適化",
      "ライブ事業の追加投資判断"
    ]
  }
}
```

## API エンドポイント

- `GET /api/reviews/quarterly/latest`: 最新四半期レビューの取得
- `GET /api/reviews/quarterly/{quarter}`: 特定四半期レビューの取得
- `POST /api/reviews/quarterly/{quarter}/generate`: 四半期レビューの生成

## Markdown 出力例

```markdown
# 四半期レビュー（2026-Q1）

## 1. 財務総括
- 売上合計: ¥3.2B （計画比 +4%）
- 営業利益: ¥410M （計画比 -2%）
- 期末キャッシュ: ¥1.8B

## 2. 実行サマリ
- 完了施策: 12
- 遅延施策: 3
- 組織負荷指数: 0.62

## 3. ギャップ分析
利益率が計画を下回った要因は、舞台制作費の増加と広告費の前倒し。

## 4. 次四半期の重点テーマ
- 制作費の最適化
- ライブ事業の追加投資判断

## 5. 取締役会レビュー
- 判定: 条件付き承認
- 理由: 利益率の改善が必要
- 条件: Q2 で利益率 1.5pt 改善を必須とする
```

## テストカバレッジ

- **test_quarterly_review_engine.py**: エンジンの各機能テスト
- **test_quarterly_review_service.py**: サービス層の生成・保存・取得テスト
- **test_quarterly_review_api.py**: API エンドポイントのテスト
- **test_dashboard_quarterly_summary.py**: ダッシュボード統合テスト

## 拡張性

- **四半期目標の動的設定**: MTPからの自動生成
- **Board レビューの詳細化**: 各取締役の専門性強化
- **KPI トラッキング**: 四半期目標の進捗可視化
- **シナリオ分析**: 複数シナリオでの四半期計画評価