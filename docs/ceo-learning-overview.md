# CEO Learning Overview

## 目的
AI CEO が過去の判断と結果から学習し、Persona を動的に変化させることで、「経験を積む経営者」になる。

## 学習の入力データ
- **財務結果**: 売上・利益・キャッシュ・投資回収感
- **市場結果**: 成長したセグメント / 伸び悩んだセグメント
- **組織結果**: 実行力・負荷・離職など
- **ガバナンス結果**: Board による「承認 / 条件付き承認 / 差し戻し」の履歴

## 学習の出力（更新されるもの）
AICeoPersona の各パラメータ：
- aggressiveness
- risk_tolerance
- brand_priority
- short_term_focus
- long_term_focus

## 学習ルール例
- 連続して利益未達 → aggressiveness を少し下げる
- Board による rejected が多い → risk_tolerance を下げる
- ブランド関連施策の成功が多い → brand_priority を上げる
- 短期利益は出ているが中期計画未達 → short_term_focus を下げ、long_term_focus を上げる

## 学習タイミング
月次バッチ（G-2）完了後に実行。

## 位置づけ
「経験を積む CEO」としての進化。最初と比べて、AI CEO の aggressiveness や risk_tolerance がどう変化したかが見えるようになる。