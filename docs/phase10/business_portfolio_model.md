# Phase 10: Business Portfolio & Investment Model

## 目的

事業ごとの成長性、収益性、市場性、競争力、リスクを評価し、AIが投資・維持・縮小・撤退・新規事業立ち上げを判断できるようにします。

## モデル構成

- `BusinessPortfolioUnit`
  - 事業単位の収益・利益・成長性・市場適合性・競争圧・リスク・投資見込み
- `InvestmentDecision`
  - 事業ごとの投資判断と予測インパクト
- `BusinessPortfolioState`
  - ある月のポートフォリオユニットと全投資判断

## 投資判断ロジック

1. 事業の収益力と成長性を外部環境・PLデータから算出
2. 競争圧・企業の強み（strategic_fit）・リスクを組み合わせ
3. 経営スタイルに応じて投資姿勢を変化させる

### 経営スタイルの違い

- Aggressive
  - 成長性が競争圧を上回れば `Invest`
  - 投資余力が薄い場合は `Maintain` や `Reduce`
- Balanced
  - 利益率と投資リターンが十分なら `Invest`
  - リスクが高ければ `Reduce`
- Conservative
  - 高リスク事業は `Reduce` または `Exit`
  - 安全性と成長性が両立すれば限定的に `Invest`

## 三位一体モデル

- 外部環境 (`environment`)
- 企業の強み (`fundamentals.profile.competitive_advantages`)
- 財務体質 (`financials.cash_reserves`)

これらを統合することで、事業ごとの投資バランスを判断します。

## ダッシュボード可視化

- 投資対象事業
- 縮小対象事業
- 撤退候補事業
- 新規事業候補
- 投資予算と残余力

### BCGマトリクス風の活用例

- High growth / high fit → Invest
- Low growth / high risk → Reduce / Exit
- Stable revenue / low investment → Maintain
- 新規市場 × 高い企業適合性 → NewBusiness
