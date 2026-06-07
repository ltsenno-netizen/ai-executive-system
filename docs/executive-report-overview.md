# Executive Report Engine Overview

Step G は、Step F で生成された Executive Narrative を受けて、月次経営レポートを Markdown 形式で自動生成するフェーズです。レポートは `/reports/YYYY-MM.md` に保存され、将来的には PDF 出力への拡張を見据えています。

## 目的

- Executive Narrative を経営レポートに昇華させる
- 経営判断の履歴と数値を分かりやすくまとめる
- ダッシュボード上から最新レポートと過去レポートへアクセスできるようにする

## フロー

1. Monthly Simulation
2. Executive Meeting (Step E)
3. Executive Narrative (Step F)
4. Executive Report Engine (Step G)
5. Markdown レポートを `/reports/YYYY-MM.md` に保存
6. Dashboard に最新レポートリンクを表示

## 出力構成

- マネジメントサマリ
- 財務ハイライト
- 市場・顧客
- 組織・実行力
- 投資・トランシェ
- リスクと注目ポイント
- 今後のフォーカス
