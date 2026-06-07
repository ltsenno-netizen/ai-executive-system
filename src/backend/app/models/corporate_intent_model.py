from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class CorporateIntent(BaseModel):
    """企業の意思（Intent）モデル - 企業が何を優先し、どのようにトレードオフを許容するかを定義"""
    
    # 目的関数の重み（合計が必ず1.0になるように正規化）
    growth_weight: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="成長重視度 (0-1)"
    )
    profitability_weight: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="収益性重視度 (0-1)"
    )
    innovation_weight: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="革新性重視度 (0-1)"
    )
    stability_weight: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="安定性重視度 (0-1)"
    )
    
    # 企業の特性
    risk_preference: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="リスク選好度 (0=超保守, 1=超攻め)"
    )
    time_horizon: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="時間軸 (0=短期, 1=長期)"
    )
    
    # 企業のアイデンティティ
    cultural_identity: str = Field(
        default="balanced",
        description="企業文化的アイデンティティ (innovative/stable/aggressive/conservative/balanced)"
    )
    mission: Optional[str] = Field(None, description="Corporate mission statement")
    vision: Optional[str] = Field(None, description="Corporate vision statement")
    values: Optional[List[str]] = Field(default_factory=list, description="Core corporate values")
    
    # メタデータ
    last_updated: Optional[datetime] = None
    update_reason: Optional[str] = None
    version: int = 1
    
    class Config:
        json_schema_extra = {
            "example": {
                "growth_weight": 0.35,
                "profitability_weight": 0.25,
                "innovation_weight": 0.25,
                "stability_weight": 0.15,
                "risk_preference": 0.6,
                "time_horizon": 0.7,
                "cultural_identity": "innovative"
            }
        }
    
    def normalize_weights(self):
        """重みを正規化（合計=1.0に）"""
        total = (
            self.growth_weight
            + self.profitability_weight
            + self.innovation_weight
            + self.stability_weight
        )
        
        if total > 0:
            self.growth_weight /= total
            self.profitability_weight /= total
            self.innovation_weight /= total
            self.stability_weight /= total


class IntentScore(BaseModel):
    """Intent ベースのスコア - Pareto frontier 上の候補の評価"""
    
    candidate_id: str = Field(description="評価される候補の ID")
    candidate_desc: str = Field(description="候補の説明（シナリオ+目的）")
    score: float = Field(description="Intent に基づいた総合スコア")
    
    # スコアの内訳
    growth_component: float = Field(description="成長に基づくスコア成分")
    profitability_component: float = Field(description="収益性に基づくスコア成分")
    innovation_component: float = Field(description="革新性に基づくスコア成分")
    stability_component: float = Field(description="安定性に基づくスコア成分")
    
    # リスクと時間軸による調整
    risk_adjustment: float = Field(description="リスク選好による調整係数")
    time_horizon_adjustment: float = Field(description="時間軸による調整係数")
    
    # 詳細情報
    breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="スコア計算の詳細な内訳"
    )


class IntentAlignment(BaseModel):
    """戦略の Intent への整合性評価"""
    
    strategy_id: str = Field(description="戦略 ID")
    strategy_desc: str = Field(description="戦略の説明")
    intent_alignment_score: float = Field(
        description="0-1 の整合性スコア（1=完全に一致）"
    )
    aligned_objectives: list = Field(
        default_factory=list,
        description="企業 Intent と一致する目的リスト"
    )
    misaligned_objectives: list = Field(
        default_factory=list,
        description="企業 Intent と相反する目的リスト"
    )
    explanation: str = Field(description="整合性の説明")


class IntentLearningHistory(BaseModel):
    """Intent 学習の歴史 - 企業が過去に選んだ戦略から学習"""
    
    cycle_count: int = Field(description="学習対象サイクル数")
    
    # 過去に選ばれた目的ベクトルの統計
    avg_growth: float = Field(description="平均成長値")
    avg_profitability: float = Field(description="平均収益性値")
    avg_innovation: float = Field(description="平均革新性値")
    avg_stability: float = Field(description="平均安定性値")
    
    # リスク傾向
    avg_risk_taken: float = Field(description="平均取得リスク")
    risk_volatility: float = Field(description="リスク取得のばらつき")
    
    # 目的の分布
    objective_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="選択された目的タイプの分布"
    )
    
    # 学習結果
    inferred_intent: Optional[CorporateIntent] = Field(
        default=None,
        description="学習から推定された企業意思"
    )
    learning_confidence: float = Field(
        default=0.0,
        description="推定の信頼度（0-1）"
    )
    
    last_learning_update: Optional[datetime] = None


class IntentAnalysis(BaseModel):
    """企業意思の詳細分析"""
    
    current_intent: CorporateIntent
    
    # Pareto frontier との関係
    frontier_score_distribution: Dict[str, float] = Field(
        default_factory=dict,
        description="各フロンティア候補のスコア分布"
    )
    
    # 最適戦略
    recommended_strategy_id: Optional[str] = None
    recommended_strategy_score: Optional[float] = None
    
    # 代替案
    alternative_strategies: list = Field(
        default_factory=list,
        description="その他の選択肢"
    )
    
    # Intent の一貫性
    intent_consistency_trend: Optional[list] = Field(
        default=None,
        description="時系列での Intent の一貫性推移"
    )
    
    # 学習履歴
    learning_history: Optional[IntentLearningHistory] = None
