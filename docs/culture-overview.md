# AI 企業文化（Culture Engine）設計

## 目的

AI 経営 OS に**企業文化**を導入して、組織の長期的な"性格"を形成する。

### 文化とは

- **意思決定の傾向** が蓄積される
- **価値観** が継承される
- **行動様式** が定着される

CEO や Board の判断傾向が蓄積されると、その企業は独自の"文化"を持つようになります。
企業が着実に"魂"を持つようになるのです。

## 設計

### 1. 文化プロファイル（CultureProfile）

```python
class CultureProfile(BaseModel):
    period: str
    aggressiveness_culture: float        # 攻め文化 (0.0-1.0)
    risk_aversion_culture: float         # 守り文化 (0.0-1.0)
    brand_culture: float                 # ブランド重視 (0.0-1.0)
    cost_culture: float                  # コスト重視 (0.0-1.0)
    people_culture: float                # 人材重視 (0.0-1.0)
    execution_culture: float             # 実行力重視 (0.0-1.0)
    innovation_culture: float            # 革新性 (0.0-1.0)
    stability_culture: float             # 安定性 (0.0-1.0)
    notes: Optional[str] = None
```

### 2. 文化更新ロジック（CultureEngine）

文化は毎月更新されます。

#### 2.1 CEO の影響（30%）

CEO の個性が直接文化に影響します：

- `aggressiveness >= 0.7` → `aggressiveness_culture +0.02`
- `brand_priority >= 0.7` → `brand_culture +0.02`
- `long_term_focus >= 0.75` → `innovation_culture +0.01`

#### 2.2 Board の影響（20%）

取締役会の判断パターンが蓄積されます：

- 拒否が多い（>= 50%） → `risk_aversion_culture +0.01`
- 承認が多い（>= 70%） → `aggressiveness_culture +0.01`

#### 2.3 四半期レビューの影響（20%）

実績が文化に反映されます：

- 実行負荷が高い（> 0.8） → `execution_culture +0.02`
- 売上が計画超過（> 10%） → `innovation_culture +0.02`
- Board 承認 → `stability_culture +0.01`

#### 2.4 自然減衰（30%）

文化は急激には変わりません。極端な文化は 0.5 に向けて緩やかに収束します：

```python
delta = culture[key] - 0.5
culture[key] = 0.5 + delta * 0.99  # 99% を保持
```

### 3. 文化が意思決定に影響する

#### 3.1 AI CEO Agent への影響

CEO は現在の文化から影響を受けます：

```python
# 攻め文化が強い → 成長スコアが上昇
aggressiveness_factor += culture.aggressiveness_culture * 0.1

# ブランド文化が強い → ブランド価値案をより高く評価
brand_score_adjustment = culture.brand_culture * 0.15

# 革新文化が強い → イノベーション案をより好む
growth_score_adjustment = culture.innovation_culture * 0.08
```

#### 3.2 Board Members への影響

各取締役も文化から影響を受けます：

**Financial Director**
- `cost_culture > 0.7` → より厳しいキャッシュ管理

**Brand Director**
- `brand_culture > 0.7` → より低い閾値でブランド案を支持

**Risk Director**
- `stability_culture > 0.7` → より厳しいリスク基準

**Org Director**
- `execution_culture > 0.75` → より高い負荷も受け入れ

### 4. 文化の保存・履歴

- 毎月 `/data/culture/{YYYY-MM}.json` に保存
- ダッシュボードで直近12ヶ月の文化推移が見える
- 文化の歴史から組織の進化をトレースできる

## 実装

### ファイル一覧

- `src/backend/app/models/culture_model.py` - CultureProfile, CultureSummary
- `src/backend/app/services/culture_engine.py` - 文化更新ロジック
- `src/backend/app/services/culture_service.py` - サービス層
- `src/backend/app/services/monthly_batch_service.py` - 月次バッチに統合
- `src/backend/app/models/executive_dashboard_model.py` - ダッシュボード統合
- `src/backend/app/services/executive_dashboard_service.py` - ダッシュボードサービス
- `src/backend/app/services/ai_ceo_agent.py` - CEO 意思決定に文化を反映
- `src/backend/app/services/ai_board_members.py` - Board 判断に文化を反映

### テスト

- `tests/test_culture_engine.py` - エンジンロジック
- `tests/test_culture_service.py` - サービス保存・読み込み
- `tests/test_dashboard_culture_summary.py` - ダッシュボード統合
- `tests/test_decision_with_culture.py` - 意思決定への影響

## 月次流れ

1. **CEO Learning**
   - CEO Persona を学習・更新

2. **CEO Succession（該当する場合）**
   - 後継 CEO を選任

3. **Culture Update** ← **NEW**
   - 前月文化を取得
   - CEO Persona を取得
   - Board 決定を取得
   - 四半期レビュー（該当する場合）を取得
   - Culture Engine で更新
   - `/data/culture/{period}.json` に保存

4. **Dashboard Build**
   - 文化サマリーを含める

## 効果

### CEO が変わっても文化は残る

```
CEO A (攻め寄り) → 文化：攻め重視 (0.65)
CEO B (守り寄り) → 文化：攻め重視 (0.62, 0.99倍減衰)
```

CEO が交代しても、前任者が作った文化は残ります。
ただし新 CEO の影響により少しずつ変化します。

### 組織が一貫性を持つ

```
会議での決定 → 文化に蓄積 → CEO・Board の判断に影響
     ↓
意思決定が一貫性を持つ
     ↓
実行結果が詰まる
     ↓
実績が文化をさらに強化
```

### ダッシュボードで文化の変化が見える

```
aggressiveness_culture: [0.50, 0.51, 0.53, 0.55, 0.58, ...]
risk_aversion_culture: [0.50, 0.49, 0.47, 0.45, 0.42, ...]
```

時系列で文化の進化をトレースできます。

## 実装例

### API

文化の更新は月次バッチで自動的に行われますが、
手動での確認・取得も可能です：

```python
from app.services.culture_service import CultureService

service = CultureService()

# 最新の文化を取得
latest_culture = service.get_latest_culture()

# 指定期間の文化を取得
culture_2026_01 = service.get_culture_for_period('2026-01')

# 文化の履歴（直近12ヶ月）
history = service.get_culture_history(periods=12)
```

### ダッシュボード

```python
{
  "month": 1,
  "culture": {
    "aggressiveness": 0.58,
    "risk_aversion": 0.45,
    "brand": 0.62,
    "cost": 0.51,
    "people": 0.55,
    "execution": 0.68,
    "innovation": 0.61,
    "stability": 0.47
  },
  ...
}
```

## まとめ

企業文化は、組織の**意思決定の傾向**が蓄積されたものです。

- CEO の個性が文化に反映される
- 文化が経営判断に影響する
- CEO が変わっても文化は残る（ただし変化する）
- 実績が文化をさらに強化する

つまり、企業は着実に"魂"を持つようになるのです。
