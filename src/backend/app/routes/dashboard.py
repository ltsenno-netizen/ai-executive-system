from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List
from ..services.dashboard_service import DashboardService

router = APIRouter()

@router.get("/dashboard/comparison")
async def compare_businesses(
    month: str = Query(..., description="対象月 (YYYY-MM形式)")
):
    """
    全事業のKPI比較
    
    Args:
        month: 対象月
        
    Returns:
        dict: 事業間比較データ
    """
    try:
        service = DashboardService()
        report = service.generate_monthly_report(month)
        
        # 事業別KPI比較表
        comparison_data = []
        for dashboard in report.business_dashboards:
            comparison_data.append({
                "business_name": dashboard.business_name,
                "revenue": dashboard.revenue_metrics.current_value,
                "profit_margin": dashboard.profit_margin_metrics.current_value,
                "cost_ratio": dashboard.cost_ratio_metrics.current_value,
                "health_score": dashboard.overall_health_score,
                "revenue_trend": dashboard.revenue_metrics.trend,
                "status": dashboard.revenue_metrics.status
            })
        
        return {
            "month": month,
            "company_health_score": report.company_health_score,
            "total_revenue": sum(d["revenue"] for d in comparison_data),
            "businesses": sorted(comparison_data, key=lambda x: x['health_score'], reverse=True),
            "insights": report.cross_business_insights,
            "alerts": report.urgent_alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/dashboard/{business_id}")
async def get_business_dashboard(
    business_id: str = Path(..., description="事業ID"),
    month: str = Query(..., description="対象月 (YYYY-MM形式)")
):
    """
    事業別KPIダッシュボードを取得
    
    Args:
        business_id: 事業ID
        month: 対象月
        
    Returns:
        KPIDashboard: KPIダッシュボード
    """
    service = DashboardService()
    dashboard = service.generate_dashboard(business_id, month)
    
    if dashboard is None:
        raise HTTPException(status_code=404, detail=f"Dashboard not found for business {business_id} in {month}")
    
    return dashboard

@router.get("/dashboard/report/{month}")
async def get_monthly_report(
    month: str = Path(..., description="対象月 (YYYY-MM形式)")
):
    """
    月次経営ダッシュボード報告書を取得
    
    経営層向けの統合レポートで以下を含む：
    - 全事業のKPIダッシュボード
    - 企業全体のヘルススコア
    - 事業間比較インサイト
    - 経営層向け戦略提案
    - 緊急アラート
    
    Args:
        month: 対象月
        
    Returns:
        DashboardReport: 月次経営ダッシュボード報告書
    """
    service = DashboardService()
    report = service.generate_monthly_report(month)
    
    return report

@router.get("/dashboard/health-score/{business_id}")
async def get_health_score(
    business_id: str = Path(..., description="事業ID"),
    month: str = Query(..., description="対象月 (YYYY-MM形式)")
):
    """
    事業のヘルススコアを取得
    
    Args:
        business_id: 事業ID
        month: 対象月
        
    Returns:
        dict: ヘルススコアと評価
    """
    try:
        service = DashboardService()
        dashboard = service.generate_dashboard(business_id, month)
        
        if dashboard is None:
            raise HTTPException(status_code=404, detail=f"Health score not found for business {business_id}")
        
        status_map = {
            "良好": "✓",
            "注意": "⚠",
            "要改善": "🔴"
        }
        
        # ヘルススコアのレベル判定
        if dashboard.overall_health_score >= 80:
            level = "Excellent"
        elif dashboard.overall_health_score >= 70:
            level = "Good"
        elif dashboard.overall_health_score >= 50:
            level = "Fair"
        else:
            level = "Poor"
        
        # ステータス判定
        if dashboard.overall_health_score >= 80:
            status = "良好"
        elif dashboard.overall_health_score >= 70:
            status = "注意"
        elif dashboard.overall_health_score >= 50:
            status = "要改善"
        else:
            status = "要改善"
        
        return {
            "business_id": business_id,
            "business_name": dashboard.business_name,
            "month": month,
            "health_score": dashboard.overall_health_score,
            "level": level,
            "revenue_trend": dashboard.revenue_metrics.trend,
            "profit_margin": dashboard.profit_margin_metrics.current_value,
            "cost_ratio": dashboard.cost_ratio_metrics.current_value,
            "status": status_map.get(status, "⚠"),
            "summary": dashboard.executive_summary,
            "key_insights": dashboard.key_insights,
            "recommendations": dashboard.recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
