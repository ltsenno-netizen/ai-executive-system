from fastapi import APIRouter, HTTPException
from typing import Optional
from ..services.quarterly_review_service import QuarterlyReviewService
from ..models.quarterly_review_model import QuarterlyReview

router = APIRouter()
service = QuarterlyReviewService()


@router.get("/api/reviews/quarterly/latest", response_model=Optional[QuarterlyReview])
async def get_latest_quarterly_review():
    """Get the latest quarterly review"""
    try:
        review = service.get_latest_quarterly_review()
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get latest quarterly review: {str(e)}")


@router.get("/api/reviews/quarterly/{quarter}", response_model=Optional[QuarterlyReview])
async def get_quarterly_review(quarter: str):
    """Get a specific quarterly review by quarter (e.g., '2026-Q1')"""
    try:
        review = service.get_quarterly_review(quarter)
        if review is None:
            raise HTTPException(status_code=404, detail=f"Quarterly review for {quarter} not found")
        return review
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quarterly review for {quarter}: {str(e)}")


@router.post("/api/reviews/quarterly/{quarter}/generate", response_model=QuarterlyReview)
async def generate_quarterly_review(quarter: str):
    """Generate a new quarterly review for the specified quarter"""
    try:
        review = service.generate_quarterly_review(quarter)
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quarterly review for {quarter}: {str(e)}")