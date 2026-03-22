from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from ..services.pl_service import PLService

router = APIRouter()

@router.get("/pl/{business_id}")
async def get_pl_statement(
    business_id: str,
    month: str = Query(..., description="対象月 (YYYY-MM形式)")
):
    """
    指定された事業・月のPLを生成して取得
    
    Args:
        business_id: 事業ID
        month: 対象月
        
    Returns:
        PLStatement: PL計算結果
    """
    service = PLService()
    pl_statement = service.generate_pl_statement(business_id, month)
    
    if pl_statement is None:
        raise HTTPException(status_code=404, detail=f"PL data not found for business {business_id} in {month}")
    
    return pl_statement

@router.post("/pl/{business_id}/simulate")
async def simulate_business_projection(
    business_id: str,
    months_ahead: int = Query(6, description="予測期間（ヶ月）"),
    growth_rate: float = Query(0.0, description="売上成長率（例: 0.05 = 5%）"),
    cost_reduction: float = Query(0.0, description="コスト削減率（例: 0.1 = 10%）")
):
    """
    事業の将来予測シミュレーションを実行
    
    Args:
        business_id: 事業ID
        months_ahead: 予測期間（ヶ月）
        growth_rate: 売上成長率
        cost_reduction: コスト削減率
        
    Returns:
        BusinessSimulation: シミュレーション結果
    """
    service = PLService()
    simulation = service.simulate_business_projection(business_id, months_ahead, growth_rate, cost_reduction)
    
    if simulation is None:
        raise HTTPException(status_code=404, detail=f"Business {business_id} not found or insufficient data")
    
    return simulation

@router.get("/pl/businesses/summary")
async def get_business_summary():
    """
    全事業のPLサマリーを取得
    
    Returns:
        List[Dict]: 事業別サマリー
    """
    service = PLService()
    summary = service.get_business_summary()
    return summary

@router.get("/pl/businesses")
async def get_all_businesses():
    """
    全事業情報を取得
    
    Returns:
        List[Business]: 全事業リスト
    """
    service = PLService()
    businesses = list(service.load_businesses().values())
    return businesses

@router.get("/pl/businesses/{business_id}")
async def get_business(business_id: str):
    """
    指定された事業情報を取得
    
    Args:
        business_id: 事業ID
        
    Returns:
        Business: 事業情報
    """
    service = PLService()
    businesses = service.load_businesses()
    
    if business_id not in businesses:
        raise HTTPException(status_code=404, detail=f"Business {business_id} not found")
    
    return businesses[business_id]