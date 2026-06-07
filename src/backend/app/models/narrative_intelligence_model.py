"""
Narrative Intelligence Models
============================

Models for narrative intelligence system that generates context-specific
narratives for different audiences based on corporate consciousness,
evolution, intent, agents, frontier, and autonomous loop integration.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .corporate_consciousness_evolution_model import ConsciousnessPhase
from .corporate_intent_model import CorporateIntent
from .executive_agent_model import ExecutiveDecisionResult
from .culture_model import CultureProfile
from .external_environment_model_v2 import ExternalEnvironmentState


class NarrativeAudience(str, Enum):
    """Audiences for which narratives are generated."""
    INVESTORS = "INVESTORS"
    EMPLOYEES = "EMPLOYEES"
    CUSTOMERS = "CUSTOMERS"
    PUBLIC = "PUBLIC"
    PARTNERS = "PARTNERS"
    CRISIS = "CRISIS"
    TRANSFORMATION = "TRANSFORMATION"
    GROWTH = "GROWTH"


class NarrativeStyle(str, Enum):
    """Styles for narrative generation."""
    FORMAL = "FORMAL"
    INSPIRATIONAL = "INSPIRATIONAL"
    ANALYTICAL = "ANALYTICAL"
    TRANSPARENT = "TRANSPARENT"
    CONFIDENT = "CONFIDENT"
    HUMBLE = "HUMBLE"


class NarrativeContext(BaseModel):
    """Context for narrative generation integrating all system components."""
    audience: NarrativeAudience = Field(..., description="Target audience for the narrative")
    style: NarrativeStyle = Field(..., description="Narrative style to use")
    phase: ConsciousnessPhase = Field(..., description="Current consciousness evolution phase")
    intent: Optional[CorporateIntent] = Field(None, description="Current corporate intent")
    decision: Optional[ExecutiveDecisionResult] = Field(None, description="Latest executive decision result")
    frontier_health: float = Field(..., ge=0.0, description="Frontier optimization health score")
    culture_profile: Optional[CultureProfile] = Field(None, description="Current culture profile")
    environment_state: Optional[ExternalEnvironmentState] = Field(None, description="Current external environment state")

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class GeneratedNarrative(BaseModel):
    """Generated narrative with metadata."""
    narrative_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique narrative identifier")
    audience: NarrativeAudience = Field(..., description="Target audience")
    style: NarrativeStyle = Field(..., description="Narrative style used")
    text: str = Field(..., description="Generated narrative text")
    key_messages: List[str] = Field(default_factory=list, description="Key messages extracted from narrative")
    tone_markers: List[str] = Field(default_factory=list, description="Tone markers detected in narrative")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class NarrativeIntelligenceMetrics(BaseModel):
    """Metrics for narrative intelligence performance."""
    total_narratives: int = Field(default=0, description="Total narratives generated")
    audience_distribution: dict = Field(default_factory=dict, description="Narratives by audience")
    style_distribution: dict = Field(default_factory=dict, description="Narratives by style")
    avg_generation_time: float = Field(default=0.0, description="Average generation time in seconds")
    last_generated: Optional[datetime] = Field(None, description="Last narrative generation timestamp")


class NarrativeIntelligenceReport(BaseModel):
    """Comprehensive report on narrative intelligence."""
    period: str = Field(..., description="Report period")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
    metrics: NarrativeIntelligenceMetrics = Field(..., description="Narrative intelligence metrics")
    recent_narratives: List[GeneratedNarrative] = Field(default_factory=list, description="Recent narratives")
    audience_effectiveness: dict = Field(default_factory=dict, description="Audience-specific effectiveness metrics")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for narrative improvement")


class NarrativeIntelligenceSummary(BaseModel):
    """Summary data for narrative intelligence dashboard integration."""
    latest_narratives: dict = Field(default_factory=dict, description="Latest narratives per audience")
    recent_audiences: List[str] = Field(default_factory=list, description="Recently addressed audiences")
    total_narratives: int = Field(default=0, description="Total narratives generated")
    last_generation: Optional[datetime] = Field(None, description="Last narrative generation timestamp")
    key_messages: List[str] = Field(default_factory=list, description="Aggregated key messages")
    tone_markers: List[str] = Field(default_factory=list, description="Aggregated tone markers")
    frontier_reflection: float = Field(default=0.0, description="Frontier reflection score")
    intent_alignment: float = Field(default=0.0, description="Intent alignment score")