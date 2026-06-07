"""
Corporate Consciousness Evolution Routes
=========================================

REST API endpoints for consciousness evolution operations.

Endpoints:
- POST /consciousness/evolution/run - Execute evolution cycle
- GET /consciousness/evolution/state - Get current evolution state
- GET /consciousness/evolution/history - Get historical evolution records
- GET /consciousness/evolution/markdown - Export evolution report as Markdown
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..models.corporate_consciousness_evolution_model import (
    ConsciousnessEvolutionState,
    ConsciousnessEvolutionMetrics,
    ConsciousnessEvolutionReport,
    ConsciousnessPhase,
)
from ..services.corporate_consciousness_evolution_service import (
    CorporateConsciousnessEvolutionService,
)
from ..services.corporate_consciousness_service import CorporateConsciousnessService
from ..services.autonomous_enterprise_service import AutonomousEnterpriseService


router = APIRouter(prefix="/consciousness/evolution", tags=["consciousness-evolution"])

# Initialize services
evolution_service = CorporateConsciousnessEvolutionService()
consciousness_service = CorporateConsciousnessService()
autonomous_service = AutonomousEnterpriseService()


@router.post("/run", response_model=Dict[str, Any])
async def run_evolution_cycle(
    with_consciousness: bool = Query(
        True,
        description="Include updated consciousness in response"
    ),
    with_events: bool = Query(
        True,
        description="Include triggering events in response"
    ),
) -> Dict[str, Any]:
    """
    Execute one consciousness evolution cycle.
    
    This endpoint orchestrates the complete evolution process:
    1. Extract triggers from environment, autonomous cycles, and culture changes
    2. Update evolution phase, momentum, and stability
    3. Apply evolution to corporate consciousness
    4. Persist state and history
    
    Args:
        with_consciousness: Include evolved consciousness in response
        with_events: Include triggering events in response
    
    Returns:
        Dictionary containing:
        - evolution_state: Updated ConsciousnessEvolutionState
        - consciousness: Updated CorporateConsciousness (if with_consciousness=True)
        - events: Triggering events (if with_events=True)
        - transition: Phase transition details if phase changed
        - status: "evolved" or "stable"
    """
    try:
        # Get current consciousness and data sources
        consciousness = consciousness_service.get_latest_consciousness()
        
        # Get autonomous cycles (mock data if service unavailable)
        autonomous_cycles = []
        try:
            latest_cycle = autonomous_service.get_latest_cycle()
            if latest_cycle:
                autonomous_cycles = [latest_cycle]
        except Exception:
            pass  # Service may not be available
        
        # Run evolution cycle
        updated_state, updated_consciousness, events = evolution_service.run_evolution_cycle(
            current_consciousness=consciousness,
            autonomous_cycles=autonomous_cycles,
            environment_events=None,  # Would come from environment service
            culture_changes=None,  # Would come from culture service
        )
        
        response = {
            "evolution_state": updated_state.model_dump(),
            "status": "evolved" if len(events) > 0 else "stable",
            "events_count": len(events),
            "timestamp": datetime.now().isoformat(),
        }
        
        if with_consciousness:
            response["consciousness"] = updated_consciousness.model_dump() if updated_consciousness else None
        
        if with_events:
            response["events"] = [
                {
                    "event_id": e.event_id,
                    "trigger_type": e.trigger_type.value,
                    "description": e.description,
                    "total_impact": e.total_impact,
                }
                for e in events
            ]
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evolution cycle failed: {str(e)}"
        )


@router.get("/state", response_model=Dict[str, Any])
async def get_evolution_state() -> Dict[str, Any]:
    """
    Get current consciousness evolution state.
    
    Returns:
        Dictionary containing:
        - current_phase: Current ConsciousnessPhase
        - momentum: Rate of consciousness change (0-1)
        - stability: Coherence and consistency (0-1)
        - last_update: Timestamp of last state update
        - total_events: Count of events in history
        - recent_events: Most recent triggering events
        - metrics: Computed evolution metrics
    """
    try:
        state = evolution_service.get_state()
        metrics = evolution_service.get_evolution_metrics(state)
        
        # Get recent events (last 5)
        recent = state.history[-5:] if state.history else []
        
        return {
            "current_phase": state.current_phase.value,
            "momentum": state.momentum,
            "stability": state.stability,
            "last_update": state.last_update.isoformat(),
            "total_events": state.total_events,
            "recent_events": [
                {
                    "event_id": e.event_id,
                    "trigger_type": e.trigger_type.value,
                    "description": e.description,
                    "timestamp": e.timestamp.isoformat(),
                    "total_impact": e.total_impact,
                }
                for e in recent
            ],
            "metrics": {
                "phase_duration_days": metrics.phase_duration_days,
                "average_event_impact": metrics.average_event_impact,
                "external_shock_frequency": metrics.external_shock_frequency,
                "internal_change_frequency": metrics.internal_change_frequency,
                "momentum_trajectory": metrics.momentum_trajectory,
                "stability_trajectory": metrics.stability_trajectory,
            },
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve evolution state: {str(e)}"
        )


@router.get("/history", response_model=Dict[str, Any])
async def get_evolution_history(
    limit: int = Query(10, ge=1, le=100, description="Maximum history records to return")
) -> Dict[str, Any]:
    """
    Get historical consciousness evolution records.
    
    Args:
        limit: Maximum number of history records to return (1-100)
    
    Returns:
        Dictionary containing:
        - total_records: Number of historical records available
        - records: Array of evolution history records
    """
    try:
        history = evolution_service.get_evolution_history(limit=limit)
        
        return {
            "total_records": len(history),
            "records": history,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve evolution history: {str(e)}"
        )


@router.get("/report", response_model=Dict[str, Any])
async def get_evolution_report(
    period: str = Query("current", description="Reporting period label")
) -> Dict[str, Any]:
    """
    Get comprehensive consciousness evolution report.
    
    Generates detailed analysis of consciousness evolution including:
    - Current phase and characteristics
    - Evolution metrics and trends
    - Recent key events
    - Strategic implications
    - Recommended actions
    - Anticipated next phase
    
    Args:
        period: Label for reporting period
    
    Returns:
        Dictionary containing evolution report data
    """
    try:
        report = evolution_service.generate_evolution_report(period=period)
        
        return {
            "period": report.period,
            "current_phase": report.current_state.current_phase.value,
            "momentum": report.current_state.momentum,
            "stability": report.current_state.stability,
            "phase_characteristics": report.phase_characteristics,
            "momentum_narrative": report.momentum_narrative,
            "stability_narrative": report.stability_narrative,
            "anticipated_next_phase": report.anticipated_next_phase.value,
            "metrics": {
                "phase_duration_days": report.metrics.phase_duration_days,
                "average_event_impact": report.metrics.average_event_impact,
                "external_shock_frequency": report.metrics.external_shock_frequency,
                "internal_change_frequency": report.metrics.internal_change_frequency,
                "momentum_trajectory": report.metrics.momentum_trajectory,
                "stability_trajectory": report.metrics.stability_trajectory,
            },
            "recent_key_events": [
                {
                    "event_id": e.event_id,
                    "trigger_type": e.trigger_type.value,
                    "description": e.description,
                    "timestamp": e.timestamp.isoformat(),
                    "total_impact": e.total_impact,
                }
                for e in report.recent_key_events
            ],
            "strategic_implications": report.strategic_implications,
            "recommended_actions": report.recommended_actions,
            "generated_at": report.generated_at.isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate evolution report: {str(e)}"
        )


@router.get("/markdown", response_model=Dict[str, Any])
async def export_evolution_markdown(
    period: str = Query("current", description="Reporting period label")
) -> Dict[str, Any]:
    """
    Export consciousness evolution report as Markdown.
    
    Generates a formatted Markdown document suitable for:
    - Stakeholder communication
    - Board presentations
    - Executive reports
    - Documentation archives
    
    Args:
        period: Label for reporting period
    
    Returns:
        Dictionary containing:
        - format: "markdown"
        - content: Full Markdown report
        - period: Reporting period
        - generated_at: Timestamp
    """
    try:
        report = evolution_service.generate_evolution_report(period=period)
        markdown = evolution_service.export_evolution_markdown(report)
        
        return {
            "format": "markdown",
            "content": markdown,
            "period": period,
            "generated_at": datetime.now().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export evolution markdown: {str(e)}"
        )
