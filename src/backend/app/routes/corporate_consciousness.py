"""
Corporate Consciousness API Routes (Step AE)

REST API endpoints for corporate consciousness:
- Generate/update consciousness
- Retrieve consciousness data
- Dashboard integration
- Export reports
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from ..services.corporate_consciousness_service import CorporateConsciousnessService

router = APIRouter()
service = CorporateConsciousnessService()


@router.post(
    "/consciousness/generate",
    tags=["Consciousness"],
    summary="Generate corporate consciousness",
    description="Generate or regenerate corporate consciousness for current period"
)
def generate_consciousness(period: str, company_name: str = "AI Executive System"):
    """
    Generate corporate consciousness.
    
    This endpoint synthesizes Intent, Agents, Frontier, Culture, History, and Environment
    into a unified corporate consciousness model expressing enterprise self-awareness.
    
    Args:
        period: Period for consciousness (e.g., "2026-01")
        company_name: Name of enterprise
    
    Returns:
        Generated consciousness with identity, purpose, direction, assessment, evolution
    """
    try:
        consciousness = service.generate_consciousness(
            period=period,
            company_name=company_name,
        )
        
        return {
            "consciousness_id": consciousness.consciousness_id,
            "period": consciousness.period,
            "company_name": consciousness.company_name,
            "overall_score": consciousness.overall_consciousness_score,
            "clarity_score": consciousness.clarity_score,
            "coherence_score": consciousness.coherence_score,
            "alignment_score": consciousness.alignment_score,
            "authenticity_score": consciousness.authenticity_score,
            "identity_statement": consciousness.self_model.identity_statement.core_identity,
            "purpose_statement": consciousness.self_model.purpose_statement.mission,
            "strategic_direction": consciousness.self_model.strategic_direction.primary_strategy,
            "created_at": consciousness.created_at,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consciousness generation failed: {str(e)}")


@router.get(
    "/consciousness/summary",
    tags=["Consciousness"],
    summary="Get consciousness summary",
    description="Get consciousness summary suitable for dashboard display"
)
def get_consciousness_summary(period: str):
    """
    Get consciousness summary for dashboard.
    
    Returns condensed consciousness information for executive dashboard display.
    
    Args:
        period: Period for consciousness
    
    Returns:
        Dashboard-ready consciousness summary
    """
    try:
        summary = service.get_consciousness_summary(period)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Consciousness not found")
        
        return {
            "consciousness_id": summary.consciousness_id,
            "period": summary.period,
            "identity_statement": summary.identity_statement,
            "purpose_statement": summary.purpose_statement,
            "strategic_direction": summary.strategic_direction,
            "current_phase": summary.current_phase,
            "next_phase": summary.next_phase,
            "overall_score": summary.overall_score,
            "clarity_score": summary.clarity_score,
            "alignment_score": summary.alignment_score,
            "top_strengths": summary.top_strengths,
            "top_challenges": summary.top_challenges,
            "strategic_implications": summary.strategic_implications,
            "consciousness_statement": summary.consciousness_statement_summary,
            "last_updated": summary.last_updated,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve consciousness summary: {str(e)}")


@router.get(
    "/consciousness/identity",
    tags=["Consciousness"],
    summary="Get identity statement",
    description="Get detailed identity statement"
)
def get_identity_statement(period: str):
    """
    Get enterprise identity statement.
    
    Returns detailed identity information including core identity, archetype,
    brand promise, and value hierarchy.
    
    Args:
        period: Period for consciousness
    
    Returns:
        Identity statement details
    """
    try:
        consciousness = service.get_consciousness(period)
        
        if not consciousness:
            consciousness = service.generate_consciousness(period, "AI Executive System")
        
        if not consciousness:
            raise HTTPException(status_code=404, detail="Consciousness not found")
        
        identity = consciousness.self_model.identity_statement
        
        return {
            "core_identity": identity.core_identity,
            "archetype": identity.cultural_archetype,
            "brand_promise": identity.brand_promise,
            "value_hierarchy": [{"value": v[0], "weight": v[1]} for v in identity.value_hierarchy],
            "founding_purpose": identity.founding_purpose,
            "current_alignment": identity.current_purpose_alignment,
            "identity_confidence": identity.identity_confidence,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve identity: {str(e)}")


@router.get(
    "/consciousness/purpose",
    tags=["Consciousness"],
    summary="Get purpose statement",
    description="Get detailed purpose statement"
)
def get_purpose_statement(period: str):
    """
    Get enterprise purpose statement.
    
    Returns mission, vision, and purpose for different stakeholders.
    
    Args:
        period: Period for consciousness
    
    Returns:
        Purpose statement details
    """
    try:
        consciousness = service.get_consciousness(period)
        
        if not consciousness:
            consciousness = service.generate_consciousness(period, "AI Executive System")
        
        if not consciousness:
            raise HTTPException(status_code=404, detail="Consciousness not found")
        
        purpose = consciousness.self_model.purpose_statement
        
        return {
            "mission": purpose.mission,
            "vision": purpose.vision,
            "purpose_articulation": purpose.purpose_articulation,
            "stakeholder_purposes": purpose.stakeholder_purposes,
            "purpose_clarity": purpose.purpose_clarity_score,
            "purpose_alignment": purpose.purpose_alignment_score,
            "evolution_trajectory": purpose.purpose_evolution_trajectory,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve purpose: {str(e)}")


@router.get(
    "/consciousness/direction",
    tags=["Consciousness"],
    summary="Get strategic direction",
    description="Get detailed strategic direction"
)
def get_strategic_direction(period: str):
    """
    Get enterprise strategic direction.
    
    Returns primary strategy, focus areas, competitive positioning, and priorities.
    
    Args:
        period: Period for consciousness
    
    Returns:
        Strategic direction details
    """
    try:
        consciousness = service.get_consciousness(period)
        
        if not consciousness:
            consciousness = service.generate_consciousness(period, "AI Executive System")
        
        if not consciousness:
            raise HTTPException(status_code=404, detail="Consciousness not found")
        
        direction = consciousness.self_model.strategic_direction
        
        return {
            "primary_strategy": direction.primary_strategy,
            "focus_areas": direction.strategic_focus_areas,
            "growth_vector": direction.growth_vector,
            "competitive_position": direction.competitive_positioning,
            "key_priorities": [{"priority": p[0], "weight": p[1]} for p in direction.key_priorities],
            "risk_posture": direction.risk_posture,
            "innovation_intensity": direction.innovation_intensity,
            "time_horizon": direction.time_horizon,
            "direction_confidence": direction.direction_confidence,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve direction: {str(e)}")


@router.get(
    "/consciousness/assessment",
    tags=["Consciousness"],
    summary="Get self-assessment",
    description="Get detailed self-assessment of enterprise"
)
def get_self_assessment(period: str):
    """
    Get enterprise self-assessment.
    
    Returns strengths, weaknesses, opportunities, threats, and dimensional assessment.
    
    Args:
        period: Period for consciousness
    
    Returns:
        Self-assessment details
    """
    try:
        consciousness = service.get_consciousness(period)
        
        if not consciousness:
            consciousness = service.generate_consciousness(period, "AI Executive System")
        
        if not consciousness:
            raise HTTPException(status_code=404, detail="Consciousness not found")
        
        assessment = consciousness.self_model.self_assessment
        
        return {
            "overall_health": assessment.overall_health,
            "maturity_level": assessment.maturity_level,
            "strengths": assessment.strengths,
            "weaknesses": assessment.weaknesses,
            "opportunities": assessment.opportunities,
            "threats": assessment.threats,
            "primary_growth_vector": assessment.primary_growth_vector,
            "primary_constraint": assessment.primary_constraint,
            "dimensions": [
                {
                    "name": d.dimension_name,
                    "current": d.current_level,
                    "desired": d.desired_level,
                    "trend": d.trend,
                    "gap": d.gap,
                    "rationale": d.rationale,
                }
                for d in assessment.dimensions
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve assessment: {str(e)}")


@router.get(
    "/consciousness/evolution",
    tags=["Consciousness"],
    summary="Get evolution trajectory",
    description="Get enterprise evolution trajectory"
)
def get_evolution_trajectory(period: str):
    """
    Get enterprise evolution trajectory.
    
    Returns historical phases, current phase, next phase, and evolutionary metrics.
    
    Args:
        period: Period for consciousness
    
    Returns:
        Evolution trajectory details
    """
    try:
        consciousness = service.get_consciousness(period)
        
        if not consciousness:
            consciousness = service.generate_consciousness(period, "AI Executive System")
        
        if not consciousness:
            raise HTTPException(status_code=404, detail="Consciousness not found")
        
        evolution = consciousness.self_model.evolution_trajectory
        
        return {
            "current_phase": evolution.current_phase_name,
            "current_characteristics": evolution.current_phase_characteristics,
            "next_phase": evolution.next_phase_anticipated,
            "phase_triggers": evolution.phase_transition_triggers,
            "learning_from_history": evolution.learning_from_history,
            "evolutionary_momentum": evolution.evolutionary_momentum,
            "adaptability_index": evolution.adaptability_index,
            "resilience_index": evolution.resilience_index,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve evolution: {str(e)}")


@router.get(
    "/consciousness/statement",
    tags=["Consciousness"],
    summary="Get consciousness statement",
    description="Get complete consciousness statement"
)
def get_consciousness_statement(period: str):
    """
    Get complete consciousness statement.
    
    Returns the generated narratives and consciousness summary.
    
    Args:
        period: Period for consciousness
    
    Returns:
        Consciousness statement
    """
    try:
        consciousness = service.get_consciousness(period)
        
        if not consciousness:
            consciousness = service.generate_consciousness(period, "AI Executive System")
        
        if not consciousness:
            raise HTTPException(status_code=404, detail="Consciousness not found")
        
        stmt = consciousness.consciousness_statement
        
        return {
            "identity_narrative": stmt.identity_narrative,
            "purpose_narrative": stmt.purpose_narrative,
            "direction_narrative": stmt.direction_narrative,
            "assessment_narrative": stmt.assessment_narrative,
            "future_narrative": stmt.future_narrative,
            "identity_one_liner": stmt.identity_one_liner,
            "purpose_one_liner": stmt.purpose_one_liner,
            "consciousness_summary": stmt.consciousness_summary,
            "generation_quality": stmt.generation_quality,
            "coherence_score": stmt.coherence_score,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve consciousness statement: {str(e)}")


@router.get(
    "/consciousness/metrics",
    tags=["Consciousness"],
    summary="Get consciousness metrics",
    description="Get comprehensive consciousness quality metrics"
)
def get_consciousness_metrics(period: str):
    """
    Get consciousness quality metrics.
    
    Returns all quality scores and metrics for consciousness.
    
    Args:
        period: Period for consciousness
    
    Returns:
        Consciousness metrics
    """
    try:
        consciousness = service.get_consciousness(period)
        
        if not consciousness:
            consciousness = service.generate_consciousness(period, "AI Executive System")
        
        if not consciousness:
            raise HTTPException(status_code=404, detail="Consciousness not found")
        
        metrics = service.compute_consciousness_metrics(consciousness)
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")


@router.get(
    "/consciousness/history",
    tags=["Consciousness"],
    summary="Get consciousness history",
    description="Get history of consciousness generations"
)
def get_consciousness_history(limit: int = 5):
    """
    Get history of consciousness generations.
    
    Args:
        limit: Number of historical records to retrieve
    
    Returns:
        List of historical consciousness records
    """
    try:
        history = service.get_consciousness_history(limit)
        return {
            "count": len(history),
            "history": history,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.get(
    "/consciousness/markdown",
    tags=["Consciousness"],
    summary="Export consciousness as markdown",
    description="Export consciousness report in markdown format"
)
def export_consciousness_markdown(period: str):
    """
    Export consciousness as markdown report.
    
    Args:
        period: Period for consciousness
    
    Returns:
        Markdown formatted report
    """
    try:
        consciousness = service.get_consciousness(period)
        
        if not consciousness:
            consciousness = service.generate_consciousness(period, "AI Executive System")
        
        if not consciousness:
            raise HTTPException(status_code=404, detail="Consciousness not found")
        
        markdown = service.export_consciousness_markdown(consciousness)
        
        return {
            "format": "markdown",
            "content": markdown,
            "period": period,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export markdown: {str(e)}")


@router.post(
    "/consciousness/update",
    tags=["Consciousness"],
    summary="Update consciousness",
    description="Update consciousness with latest data"
)
def update_consciousness(period: str, company_name: str = "AI Executive System"):
    """
    Update consciousness with latest data.
    
    Regenerates consciousness using current Intent, Agents, Frontier, Culture, etc.
    
    Args:
        period: Period for consciousness
        company_name: Enterprise name
    
    Returns:
        Updated consciousness
    """
    try:
        consciousness = service.update_consciousness(
            period=period,
            company_name=company_name,
        )
        
        return {
            "consciousness_id": consciousness.consciousness_id,
            "period": consciousness.period,
            "status": "updated",
            "overall_score": consciousness.overall_consciousness_score,
            "clarity_score": consciousness.clarity_score,
            "coherence_score": consciousness.coherence_score,
            "alignment_score": consciousness.alignment_score,
            "updated_at": datetime.now(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consciousness update failed: {str(e)}")
