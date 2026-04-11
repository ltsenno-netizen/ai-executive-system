# Phase 2.5：会社経営モデル × 年間オペレーションモデル 統合レイヤー

## 目的
Phase 1 の `company_operating_model` と Phase 2 の `annual_operations_model` を連携し、
「1ヶ月進めると、PL・キャッシュ・部門負荷・タスク・インシデントが一括で更新される」
統合シミュレーションAPIを提供する。

## 統合の流れ

1. `CompanyOperatingService.load_company_model()` で会社経営モデルを読み込む
2. `AnnualOperationsService.load_operations_model()` で年間オペレーションモデルを読み込む
3. `CompanyOperatingService.simulate_month(month)` でPL・キャッシュ・KPIを計算する
4. `AnnualOperationsService.simulate_month_operations(month)` で部門負荷・タスク・インシデントを生成する
5. `CompanyOperationsIntegrationService.simulate_month_full(month)` で両者を統合する

## 出力JSON構造

```json
{
  "month": 7,
  "pl": {
    "month": 7,
    "revenue": { ... },
    "cost": { ... },
    "profit": 2.1,
    "profit_margin": 0.14,
    "cash_flow": -1.2,
    "cash_balance": 38.2,
    "kpis": {
      "gross_profit": 4.0,
      "operating_profit": 2.1,
      "license_ratio": 0.125,
      "digital_ratio": 0.13,
      "talent_ltv_index": 1.0
    }
  },
  "operations": {
    "month": 7,
    "department_load": {
      "talent_management": 1.1,
      "performance": 1.3,
      "rights": 0.65,
      "management": 0.55
    },
    "generated_tasks": [ ... ],
    "generated_incidents": [ ... ]
  },
  "strategy": {}
}
```

## 「1ヶ月進める」と何が起きるか

- PL側
  - 月次売上・費用の計算が確定する
  - 投資支出がキャッシュフローに反映される
  - KPI が月次単位で更新される

- オペレーション側
  - 月次イベントに応じた部門負荷が決定される
  - 部門ごとのタスクが自動生成される
  - インシデントリスクが発生し、緊急対応が必要になる

## 部門負荷の例

- タレントマネジメント部
  - 1〜3月：契約更新期で負荷高め
  - 7〜9月：公演期のサポート業務として高負荷
  - 11〜12月：MD・広告施策の対応増加

- 公演事業本部
  - 7〜9月：公演ピークに連動して負荷上昇
  - 4〜6月：新番組立ち上げ準備段階で負荷が高まる

- ライツ本部
  - 10〜12月：ライセンス締結期・広告連動で負荷増
  - 1〜3月：年始の契約更新で安定的に一定の負荷

## 今後の Phase 3 での拡張

- 本統合結果に `strategy` 要素を追加し、
  - 中期戦略目標とのギャップ評価
  - 戦略KPIと実績の差分分析
  - 方針変更シナリオの提案

この設計により、Phase 3 では `month` ごとの統合結果に strategy レイヤーを乗せるだけで、
戦略評価まで一気通貫で拡張できる。