from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.corporate_intent_service import CorporateIntentService
from ..models.corporate_intent_model import CorporateIntent

router = APIRouter(tags=["corporate-intent"])
intent_service = CorporateIntentService()


class SetIntentRequest(BaseModel):
    growth_weight: float
    profitability_weight: float
    innovation_weight: float
    stability_weight: float
    risk_preference: float
    time_horizon: float
    cultural_identity: str


@router.get("/intent")
def get_intent():
    """現在の企業意思を取得"""
    intent = intent_service.get_intent()
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    return intent


@router.post("/intent/update")
def update_intent():
    """過去のサイクルから学習して企業意思を更新"""
    try:
        updated_intent = intent_service.update_intent_from_learning()
        return {
            "message": "Intent updated from learning history",
            "intent": updated_intent,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intent/set")
def set_intent(request: SetIntentRequest):
    """企業意思を明示的に設定"""
    try:
        new_intent = intent_service.set_intent(
            growth_weight=request.growth_weight,
            profitability_weight=request.profitability_weight,
            innovation_weight=request.innovation_weight,
            stability_weight=request.stability_weight,
            risk_preference=request.risk_preference,
            time_horizon=request.time_horizon,
            cultural_identity=request.cultural_identity,
        )
        return {
            "message": "Intent set successfully",
            "intent": new_intent,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/intent/analysis")
def analyze_intent():
    """企業意思の詳細分析"""
    try:
        analysis = intent_service.analyze_intent()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intent/optimal-strategy")
def get_optimal_strategy():
    """現在の意思に基づいて最適戦略を取得"""
    try:
        candidate, score = intent_service.select_optimal_strategy()
        return {
            "message": "Optimal strategy selected based on Intent",
            "strategy": candidate,
            "score": score,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intent/ranked-strategies")
def get_ranked_strategies():
    """企業意思に基づいて全戦略をランク付け"""
    try:
        ranked = intent_service.rank_strategies()
        return {
            "count": len(ranked),
            "ranked_strategies": [
                {
                    "candidate": candidate.model_dump(),
                    "score": score.model_dump(),
                }
                for candidate, score in ranked
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intent/alignment/{candidate_id}")
def get_alignment(candidate_id: str):
    """特定の戦略の意思への整合性を分析"""
    try:
        alignment = intent_service.get_alignment_analysis(candidate_id)
        if not alignment:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return alignment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intent/markdown")
def get_intent_markdown():
    """企業意思を Markdown 形式で取得"""
    try:
        md = intent_service.export_intent_to_markdown()
        return {"markdown": md}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
