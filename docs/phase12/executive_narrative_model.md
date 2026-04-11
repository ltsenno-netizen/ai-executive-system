# Phase 12: Executive Narrative Engine

## 経営ストーリーの役割

AI Executive Narrative Engine は、月次・年次・複数年の経営変化を因果関係と企業の性格を反映した物語として提供します。数字の羅列ではなく、外部環境や内部改善、経営判断のつながりを経営者が直感的に理解できる形にまとめます。

## Monthly / Annual / Multi-Year の違い

- MonthlyNarrative
  - 1ヶ月の経営ストーリーを「外部環境」「課題と意思決定」「結果と見通し」の3つの章で構成
  - sentiment、key_drivers、risks、opportunities を含む
  - 経営会議とポートフォリオ判断を必ず盛り込む

- AnnualNarrative
  - 12ヶ月の月次ストーリーを集約し、年間を通じた変化の流れを描く
  - 事業ユニットごとのストーリー、戦略の変化、翌年の展望を示す

- MultiYearNarrative
  - 複数年に渡る企業の変革軌跡を描く
  - 企業の歴史と成長要因、構造変化、長期展望を統合する

## ストーリー生成ロジック

1. 月次データを収集
   - PL サマリー、KPI、Operations、Issues、Improvements
   - Portfolio Decisions、Meeting Decisions
   - External Environment、Corporate Fundamentals

2. 経営ストーリーを構成
   - 外部環境→課題→改善→投資→結果、という因果関係の流れを作る
   - 企業の強みや経営スタイルを語り口として反映
   - 会議での意思決定を必ずストーリーに反映

3. sentiment の算出
   - 利益率・収益・課題数・重大課題を組み合わせて「Positive」「Neutral」「Negative」を判断

4. 年次と複数年ストーリー
   - 年次は月次の連続性から主要イベントと戦略転換を抽出
   - 複数年は企業歴史と成長ドライバーを統合し、変化の軸を描く

## 経営者がストーリーから読み取るべきポイント

- なぜ今この意思決定が必要だったのか
- 外部環境と内部改善のどちらが変化を牽引しているのか
- どのリスクが現実的で、どの機会を優先すべきか
- 今後の戦略転換と次年度の見通し

## ダッシュボードでの活用例

- 月次ダッシュボードに narrative_summary を追加
  - story_highlights
  - sentiment
  - key_drivers
  - risks
  - opportunities

- 経営トップは数値だけでなくストーリーを確認し、意思決定の背景を直感的に比較できる
- 会議前にストーリーを読み、意思決定の文脈とリスク・機会を整理する
