"""
Narrative Intelligence API Routes
=================================

REST API endpoints for narrative intelligence operations including
generation, retrieval, history, and export functionality.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from ..models.narrative_intelligence_model import (
    GeneratedNarrative,
    NarrativeAudience,
    NarrativeIntelligenceMetrics,
    NarrativeIntelligenceReport,
    NarrativeStyle,
)
from ..services.narrative_intelligence_service import NarrativeIntelligenceService

router = APIRouter()
service = NarrativeIntelligenceService()


@router.post(
    "/narrative/generate/{audience}",
    response_model=GeneratedNarrative,
    summary="Generate Narrative",
    description="Generate a narrative for the specified audience based on current corporate context."
)
async def generate_narrative(audience: NarrativeAudience) -> GeneratedNarrative:
    """
    Generate a narrative for the specified audience.

    This endpoint integrates data from consciousness, evolution, intent, agents,
    frontier, and autonomous loop to create contextually appropriate narratives.

    Args:
        audience: Target audience for the narrative

    Returns:
        GeneratedNarrative: The generated narrative with metadata
    """
    try:
        narrative = service.generate_narrative(audience)
        return narrative
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate narrative: {str(e)}")


@router.get(
    "/narrative/{narrative_id}",
    response_model=GeneratedNarrative,
    summary="Get Narrative",
    description="Retrieve a specific narrative by its ID."
)
async def get_narrative(narrative_id: str) -> GeneratedNarrative:
    """
    Retrieve a specific narrative by ID.

    Args:
        narrative_id: Unique identifier of the narrative

    Returns:
        GeneratedNarrative: The requested narrative

    Raises:
        HTTPException: If narrative is not found
    """
    narrative = service.get_narrative(narrative_id)
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return narrative


@router.get(
    "/narrative/history",
    response_model=List[GeneratedNarrative],
    summary="Get Narrative History",
    description="Retrieve the history of generated narratives."
)
async def get_narrative_history(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of narratives to return")
) -> List[GeneratedNarrative]:
    """
    Get narrative generation history.

    Args:
        limit: Maximum number of narratives to return (1-200)

    Returns:
        List[GeneratedNarrative]: Recent narratives sorted by timestamp
    """
    return service.get_narrative_history(limit)


@router.get(
    "/narrative/{narrative_id}/markdown",
    response_class=PlainTextResponse,
    summary="Export Narrative as Markdown",
    description="Export a narrative in markdown format for documentation or sharing."
)
async def export_narrative_markdown(narrative_id: str) -> str:
    """
    Export a narrative as markdown.

    Args:
        narrative_id: Unique identifier of the narrative

    Returns:
        str: Markdown formatted narrative

    Raises:
        HTTPException: If narrative is not found
    """
    markdown = service.export_narrative_markdown(narrative_id)
    if not markdown:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return markdown


@router.get(
    "/narrative/audiences",
    response_model=List[dict],
    summary="Get Available Audiences",
    description="Get the list of available narrative audiences."
)
async def get_available_audiences() -> List[dict]:
    """
    Get available narrative audiences.

    Returns:
        List[dict]: List of audiences with descriptions
    """
    audiences = [
        {
            "audience": audience.value,
            "description": NarrativeIntelligenceService._get_audience_description(audience)
        }
        for audience in NarrativeAudience
    ]
    return audiences


@router.get(
    "/narrative/styles",
    response_model=List[dict],
    summary="Get Available Styles",
    description="Get the list of available narrative styles."
)
async def get_available_styles() -> List[dict]:
    """
    Get available narrative styles.

    Returns:
        List[dict]: List of styles with descriptions
    """
    styles = [
        {
            "style": style.value,
            "description": NarrativeIntelligenceService._get_style_description(style)
        }
        for style in NarrativeStyle
    ]
    return styles


@router.get(
    "/narrative/metrics",
    response_model=NarrativeIntelligenceMetrics,
    summary="Get Narrative Metrics",
    description="Get metrics about narrative intelligence performance."
)
async def get_narrative_metrics() -> NarrativeIntelligenceMetrics:
    """
    Get narrative intelligence metrics.

    Returns:
        NarrativeIntelligenceMetrics: Current metrics and statistics
    """
    return service.get_narrative_metrics()


@router.get(
    "/narrative/report",
    response_model=NarrativeIntelligenceReport,
    summary="Generate Narrative Report",
    description="Generate a comprehensive report on narrative intelligence."
)
async def generate_narrative_report(
    period: str = Query("last_30_days", description="Report period")
) -> NarrativeIntelligenceReport:
    """
    Generate a comprehensive narrative intelligence report.

    Args:
        period: Time period for the report

    Returns:
        NarrativeIntelligenceReport: Complete report with metrics and recommendations
    """
    return service.generate_narrative_report(period)


@router.get(
    "/narrative/audience/{audience}",
    response_model=List[GeneratedNarrative],
    summary="Get Narratives by Audience",
    description="Get all narratives for a specific audience."
)
async def get_narratives_by_audience(
    audience: NarrativeAudience,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of narratives to return")
) -> List[GeneratedNarrative]:
    """
    Get narratives for a specific audience.

    Args:
        audience: Target audience
        limit: Maximum number of narratives to return

    Returns:
        List[GeneratedNarrative]: Narratives for the specified audience
    """
    return service.get_narratives_by_audience(audience, limit)


# Helper methods for descriptions (would typically be in a separate utility module)
class NarrativeIntelligenceService:
    """Helper class for API descriptions."""

    @staticmethod
    def _get_audience_description(audience: NarrativeAudience) -> str:
        """Get description for an audience."""
        descriptions = {
            NarrativeAudience.INVESTORS: "Financial stakeholders and investment community",
            NarrativeAudience.EMPLOYEES: "Internal workforce and organizational members",
            NarrativeAudience.CUSTOMERS: "Current and potential customers",
            NarrativeAudience.PUBLIC: "General public and society",
            NarrativeAudience.PARTNERS: "Business partners and collaborators",
            NarrativeAudience.CRISIS: "Stakeholders during crisis situations",
            NarrativeAudience.TRANSFORMATION: "Audiences during major organizational change",
            NarrativeAudience.GROWTH: "Stakeholders during growth and expansion phases",
        }
        return descriptions.get(audience, "General audience")

    @staticmethod
    def _get_style_description(style: NarrativeStyle) -> str:
        """Get description for a style."""
        descriptions = {
            NarrativeStyle.FORMAL: "Professional and structured communication",
            NarrativeStyle.INSPIRATIONAL: "Motivational and vision-driven messaging",
            NarrativeStyle.ANALYTICAL: "Data-driven and logical presentation",
            NarrativeStyle.TRANSPARENT: "Open and honest disclosure",
            NarrativeStyle.CONFIDENT: "Assured and self-assured tone",
            NarrativeStyle.HUMBLE: "Modest and grounded approach",
        }
        return descriptions.get(style, "General communication style")