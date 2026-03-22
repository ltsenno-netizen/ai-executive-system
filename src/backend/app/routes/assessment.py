from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict, Any
from ..services.assessment_service import AssessmentService

router = APIRouter()

@router.post("/assessment/{member_id}/generate-case")
async def generate_assessment_case(
    member_id: int,
    difficulty: str = "intermediate"
):
    """
    メンバーのプロフィールに基づいてアセスメントケースを生成
    
    Args:
        member_id: メンバーのID
        difficulty: 難易度 ("basic", "intermediate", "advanced")
        
    Returns:
        AssessmentCase: 生成されたアセスメントケース
    """
    service = AssessmentService()
    case = service.generate_case(member_id, difficulty)
    
    if case is None:
        raise HTTPException(status_code=404, detail=f"Member with id {member_id} not found")
    
    return case

@router.post("/assessment/{member_id}/evaluate")
async def evaluate_assessment_answer(
    member_id: int,
    case_id: str = Body(..., embed=True),
    answer_text: str = Body(..., embed=True)
):
    """
    アセスメント回答を評価し、フィードバックを生成
    
    Args:
        member_id: メンバーのID
        case_id: ケースID
        answer_text: 回答テキスト
        
    Returns:
        AssessmentFeedback: 評価結果とフィードバック
    """
    service = AssessmentService()
    feedback = service.evaluate_answer(case_id, member_id, answer_text)
    
    if feedback is None:
        raise HTTPException(status_code=404, detail="Case or member not found")
    
    return feedback

@router.get("/assessment/{member_id}/recommended-cases")
async def get_recommended_cases(member_id: int):
    """
    メンバーの成長段階に合ったおすすめケースを取得
    
    Args:
        member_id: メンバーのID
        
    Returns:
        List[AssessmentCase]: おすすめケースのリスト
    """
    service = AssessmentService()
    cases = service.get_recommended_cases(member_id)
    return cases

@router.get("/assessment/{member_id}/progress")
async def get_assessment_progress(member_id: int):
    """
    メンバーのアセスメント練習進捗を取得
    
    Args:
        member_id: メンバーのID
        
    Returns:
        AssessmentPractice: 練習進捗データ
    """
    service = AssessmentService()
    progress = service.get_practice_progress(member_id)
    
    if progress is None:
        raise HTTPException(status_code=404, detail=f"No practice data found for member {member_id}")
    
    return progress

@router.get("/assessment/cases/{case_id}")
async def get_assessment_case(case_id: str):
    """
    指定されたケースを取得
    
    Args:
        case_id: ケースID
        
    Returns:
        AssessmentCase: アセスメントケース
    """
    service = AssessmentService()
    cases = service.load_cases()
    
    if case_id not in cases:
        raise HTTPException(status_code=404, detail=f"Case with id {case_id} not found")
    
    return cases[case_id]

@router.get("/assessment/cases")
async def get_all_cases():
    """
    全てのアセスメントケースを取得
    
    Returns:
        List[AssessmentCase]: 全ケースのリスト
    """
    service = AssessmentService()
    cases = list(service.load_cases().values())
    return cases