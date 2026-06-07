"""
Multi-Company Comparative API Routes (Step AK)

REST endpoints for multi-company comparison intelligence.
"""

from typing import Dict, List
from fastapi import APIRouter, HTTPException

from ..models.multi_company_comparative_model import (
    CompanyId,
    MultiCompanyComparisonReport,
    MultiCompanyComparisonSummary,
)
from ..services.multi_company_comparative_service import MultiCompanyComparativeService

router = APIRouter(prefix="/companies", tags=["multi-company-comparative"])
service = MultiCompanyComparativeService()


@router.get("")
async def list_available_companies() -> Dict[str, object]:
    """Get list of available companies for comparison."""
    try:
        companies = service.list_available_companies()
        return {
            "companies": [c.model_dump() for c in companies],
            "count": len(companies),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_companies(company_ids: List[CompanyId]) -> MultiCompanyComparisonReport:
    """
    Generate a comparative analysis of multiple companies.

    Request body: List of CompanyId objects
    Returns: MultiCompanyComparisonReport
    """
    try:
        if not company_ids:
            raise HTTPException(status_code=400, detail="At least one company required")

        if len(company_ids) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 companies per comparison")

        report = service.compare_companies(company_ids)
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/latest")
async def get_latest_comparison() -> Dict[str, object]:
    """Get the most recent comparison report."""
    try:
        report = service.get_last_comparison()
        if report is None:
            raise HTTPException(status_code=404, detail="No comparison reports available")

        return report.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/{report_id}")
async def get_comparison_report(report_id: str) -> Dict[str, object]:
    """Get a specific comparison report by ID."""
    try:
        report = service.get_report_by_id(report_id)
        if report is None:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

        return report.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/{report_id}/markdown")
async def get_comparison_markdown(report_id: str) -> Dict[str, str]:
    """Get a comparison report in markdown format."""
    try:
        report = service.get_report_by_id(report_id)
        if report is None:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

        markdown = service.generate_markdown_report(report)
        return {
            "report_id": report_id,
            "format": "markdown",
            "content": markdown,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/latest/summary")
async def get_latest_comparison_summary() -> MultiCompanyComparisonSummary:
    """Get a dashboard-friendly summary of the latest comparison."""
    try:
        report = service.get_last_comparison()
        if report is None:
            raise HTTPException(status_code=404, detail="No comparison reports available")

        # Find strongest and weakest
        all_scores = {}
        for metric in report.metrics:
            for company_id, value in metric.values.items():
                if company_id not in all_scores:
                    all_scores[company_id] = []
                all_scores[company_id].append(value)

        avg_scores = {cid: sum(scores) / len(scores) for cid, scores in all_scores.items()}
        strongest = max(avg_scores, key=avg_scores.get) if avg_scores else None
        weakest = min(avg_scores, key=avg_scores.get) if avg_scores else None

        cluster_dict = {c.cluster_name: c.company_ids for c in report.clusters}

        summary = MultiCompanyComparisonSummary(
            companies=[c.name for c in report.companies],
            strongest_company=strongest,
            weakest_company=weakest,
            cluster_count=len(report.clusters),
            cluster_labels=cluster_dict,
            key_insight=report.narrative_summary.split("\n")[0] if report.narrative_summary else "No insights",
            last_compared=report.comparison_date,
        )

        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
