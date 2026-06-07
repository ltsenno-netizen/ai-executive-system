# Executive Team Succession Overview

## 目的
CEO だけでなく、CFO / COO / CMO / CHRO の 4 名も学習し、後継者が生まれ、交代する仕組みを導入する。

これにより：
- 経営チーム全体が経験を積む
- 経営チームの構成が企業文化に影響
- 外部環境に応じて適切な後継者が選ばれる
- 経営チームの世代交代が企業の"歴史"を形成
- 企業シミュレーションとしての深みが一気に増す。

## 各役職の役割
- **CFO (Chief Financial Officer)**: 財務戦略、資金調達、リスク管理
- **COO (Chief Operating Officer)**: 業務運営、効率化、実行力
- **CMO (Chief Marketing Officer)**: ブランド戦略、市場開拓、顧客獲得
- **CHRO (Chief Human Resources Officer)**: 人材戦略、組織文化、従業員エンゲージメント

## 後継者生成ロジック
各役職ごとに3名の候補者を生成：
- **Candidate A（継承型）**: 現在の役員に近いスタイル。安定性重視。
- **Candidate B（攻め型）**: 革新性を高め、成長を促進。innovation_bias +0.1、役職に応じたフォーカス強化。
- **Candidate C（守り型）**: リスク管理を強化。risk_tolerance -0.1、安定性重視。

## Board の選任プロセス
取締役会が各役職の候補者から選任：
- **Financial Director**: CFO の候補を厳しく評価
- **Org Director**: CHRO の候補を重視
- **Brand Director**: CMO の候補を重視
- **Risk Director**: 全役職のリスクを評価

最多得票者が選ばれる。

## 経営チームの世代交代の例
- 不況期: CFO が守り型に交代、財務保守化
- 成長期: CMO が攻め型に交代、ブランド拡大
- 文化変化: people_culture 高まりで CHRO が強化
- 技術革新: COO が革新型に交代、業務効率化

## 外部環境・文化との関係
- **経済環境**: 不況時は CFO/COO の保守化
- **競争環境**: 激化時は CMO の革新性
- **企業文化**: people_culture 高まりで CHRO 強化
- **技術変化**: innovation_culture で全役職の革新性向上