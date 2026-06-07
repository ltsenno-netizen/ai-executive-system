from typing import Optional
from pydantic import BaseModel, Field


class CultureProfile(BaseModel):
    """
    企業文化プロファイル
    CEO と Board の判断傾向、価値観が蓄積される
    """
    period: str
    aggressiveness_culture: float = Field(..., ge=0.0, le=1.0, description="攻め文化度")
    risk_aversion_culture: float = Field(..., ge=0.0, le=1.0, description="守り文化度")
    brand_culture: float = Field(..., ge=0.0, le=1.0, description="ブランド重視")
    cost_culture: float = Field(..., ge=0.0, le=1.0, description="コスト重視")
    people_culture: float = Field(..., ge=0.0, le=1.0, description="人材重視")
    execution_culture: float = Field(..., ge=0.0, le=1.0, description="実行力重視")
    innovation_culture: float = Field(..., ge=0.0, le=1.0, description="革新性")
    stability_culture: float = Field(..., ge=0.0, le=1.0, description="安定性")
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "period": "2026-01",
                "aggressiveness_culture": 0.6,
                "risk_aversion_culture": 0.4,
                "brand_culture": 0.7,
                "cost_culture": 0.5,
                "people_culture": 0.6,
                "execution_culture": 0.7,
                "innovation_culture": 0.5,
                "stability_culture": 0.5,
                "notes": "CEO の攻め姿勢が反映。組織は実行力を重視。"
            }
        }


class CultureSummary(BaseModel):
    """ダッシュボード用の文化サマリー"""
    aggressiveness: float
    risk_aversion: float
    brand: float
    cost: float
    people: float
    execution: float
    innovation: float
    stability: float
