from fastapi import APIRouter, HTTPException
from typing import Optional
from ..services.corporate_story_service import CorporateStoryService

router = APIRouter(prefix="/story", tags=["story"])
service = CorporateStoryService()


@router.post("/generate/{period}")
async def generate_story(period: str):
    """指定期間の企業ストーリーを生成"""
    try:
        story = service.generate_story(period)
        return {
            "message": f"Generated corporate story for period: {period}",
            "story": story.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{period}")
async def get_story(period: str):
    """指定期間のストーリーを取得"""
    try:
        story = service.get_story(period)
        if story is None:
            raise HTTPException(status_code=404, detail=f"Story not found for period: {period}")
        return story.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_latest_story():
    """最新のストーリーを取得"""
    try:
        story = service.get_latest_story()
        if story is None:
            raise HTTPException(status_code=404, detail="No story found")
        return story.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
