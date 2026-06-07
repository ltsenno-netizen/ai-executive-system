"""
Corporate Consciousness Model (Step AE)

Models for enterprise self-awareness and consciousness generation:
- Corporate Self-Model: Integration of all enterprise state
- Consciousness statements: Identity, purpose, direction, assessment
- Meta-decision synthesis: Enterprise purpose redefinition
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field


class SelfAssessmentDimension(BaseModel):
    """Assessment of enterprise along one dimension"""
    dimension_name: str
    current_level: float = Field(ge=0.0, le=1.0)
    desired_level: float = Field(ge=0.0, le=1.0)
    trend: str = Field(description="improving, stable, declining")
    rationale: str
    gap: float = Field(ge=-1.0, le=1.0, description="desired - current")


class SelfAssessment(BaseModel):
    """Comprehensive self-assessment of enterprise"""
    assessment_id: str
    period: str
    
    strengths: List[str] = Field(description="Enterprise strengths")
    weaknesses: List[str] = Field(description="Enterprise weaknesses")
    opportunities: List[str] = Field(description="Strategic opportunities")
    threats: List[str] = Field(description="External threats")
    
    dimensions: List[SelfAssessmentDimension] = Field(
        description="Multi-dimensional assessment (growth, profit, innovation, stability, health, agility)"
    )
    
    overall_health: float = Field(ge=0.0, le=1.0, description="Overall enterprise health score")
    maturity_level: str = Field(
        description="startup/growing/established/mature/transforming"
    )
    
    primary_growth_vector: str = Field(description="Primary direction of growth")
    primary_constraint: str = Field(description="Primary limiting factor")
    
    created_at: datetime = Field(default_factory=datetime.now)


class IdentityStatement(BaseModel):
    """Statement of corporate identity"""
    statement_id: str
    period: str
    
    core_identity: str = Field(description="What the enterprise fundamentally is")
    cultural_archetype: str = Field(
        description="archetypal pattern: innovator/leader/challenger/protector/caregiver/sage/magician/lover"
    )
    brand_promise: str = Field(description="What the enterprise promises to stakeholders")
    
    value_hierarchy: List[Tuple[str, float]] = Field(
        description="Ranked list of core values and importance weights"
    )
    
    founding_purpose: Optional[str] = Field(description="Original founding purpose if known")
    current_purpose_alignment: float = Field(
        ge=0.0, le=1.0, description="How aligned current operations are with founding purpose"
    )
    
    identity_confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence level in identity clarity"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)


class PurposeStatement(BaseModel):
    """Statement of enterprise purpose"""
    statement_id: str
    period: str
    
    mission: str = Field(description="Why the enterprise exists")
    vision: str = Field(description="What the enterprise aspires to become")
    purpose_articulation: str = Field(description="How the enterprise expresses its fundamental purpose")
    
    stakeholder_purposes: Dict[str, str] = Field(
        description="How purpose is articulated to different stakeholders (employees, customers, investors, society)"
    )
    
    purpose_clarity_score: float = Field(
        ge=0.0, le=1.0, description="How clearly the purpose is defined"
    )
    purpose_alignment_score: float = Field(
        ge=0.0, le=1.0, description="How well purpose aligns with actions"
    )
    
    purpose_evolution_trajectory: str = Field(
        description="How purpose is expected to evolve"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)


class StrategicDirection(BaseModel):
    """Statement of strategic direction"""
    direction_id: str
    period: str
    
    primary_strategy: str = Field(description="Primary strategic approach")
    strategic_focus_areas: List[str] = Field(description="Key focus areas for next period")
    
    growth_vector: str = Field(description="Primary direction of growth")
    competitive_positioning: str = Field(
        description="Intended competitive position (leader/challenger/niche/hidden champion)"
    )
    
    key_priorities: List[Tuple[str, float]] = Field(
        description="Key priorities and relative importance"
    )
    
    strategic_flexibility: float = Field(
        ge=0.0, le=1.0, description="Ability to adapt strategy if needed"
    )
    risk_posture: str = Field(description="risk-averse/balanced/aggressive")
    innovation_intensity: str = Field(description="conservative/incremental/disruptive")
    
    time_horizon: str = Field(description="short-term/medium-term/long-term focus")
    
    direction_confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in strategic direction"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)


class EvolutionTrajectory(BaseModel):
    """Model of enterprise evolution over time"""
    trajectory_id: str
    period: str
    
    historical_phases: List[Dict[str, str]] = Field(
        description="Historical phases (phase_name, duration, key_characteristics, outcome)"
    )
    
    current_phase_name: str = Field(description="Name of current evolution phase")
    current_phase_characteristics: str = Field(description="Characteristics of current phase")
    
    next_phase_anticipated: str = Field(description="Expected next phase")
    phase_transition_triggers: List[str] = Field(
        description="Events/conditions that would trigger phase transition"
    )
    
    learning_from_history: List[str] = Field(
        description="Key lessons from enterprise history"
    )
    
    evolutionary_momentum: float = Field(
        ge=-1.0, le=1.0, description="Velocity of change (-1=declining, 0=stable, 1=rapidly evolving)"
    )
    
    adaptability_index: float = Field(
        ge=0.0, le=1.0, description="Ability to adapt and evolve"
    )
    
    resilience_index: float = Field(
        ge=0.0, le=1.0, description="Ability to withstand challenges"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)


class MetaDecisionSynthesis(BaseModel):
    """Synthesis of Intent, Agents, and Frontier into unified purpose"""
    synthesis_id: str
    period: str
    
    intent_contribution: Dict[str, float] = Field(
        description="How corporate intent (weights) influences meta-decision"
    )
    agent_contribution: Dict[str, str] = Field(
        description="How agent consensus influences meta-decision (agent_role -> contribution_summary)"
    )
    frontier_contribution: Dict[str, float] = Field(
        description="How frontier optimization influences meta-decision (analysis_type -> contribution_score)"
    )
    
    culture_influence: Dict[str, float] = Field(
        description="How culture influences meta-decision"
    )
    history_influence: str = Field(
        description="How history influences meta-decision"
    )
    environment_influence: str = Field(
        description="How external environment influences meta-decision"
    )
    
    unified_direction: str = Field(
        description="Unified direction synthesized from all sources"
    )
    
    consensus_level: float = Field(
        ge=0.0, le=1.0, description="How well components agree on direction"
    )
    
    synthesis_confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in synthesis quality"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)


class CorporateSelfModel(BaseModel):
    """Integrated model of corporate self"""
    model_id: str
    period: str
    
    # Core state
    identity_statement: IdentityStatement
    purpose_statement: PurposeStatement
    strategic_direction: StrategicDirection
    self_assessment: SelfAssessment
    evolution_trajectory: EvolutionTrajectory
    meta_decision: MetaDecisionSynthesis
    
    # Metadata
    model_coherence: float = Field(
        ge=0.0, le=1.0, description="Internal coherence of model (do components align?)"
    )
    self_awareness_level: float = Field(
        ge=0.0, le=1.0, description="Clarity of self-understanding"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class ConsciousnessStatement(BaseModel):
    """Generated consciousness statement - what the enterprise says about itself"""
    statement_id: str
    period: str
    
    identity_narrative: str = Field(
        description="Narrative about who the enterprise is"
    )
    purpose_narrative: str = Field(
        description="Narrative about why the enterprise exists"
    )
    direction_narrative: str = Field(
        description="Narrative about where the enterprise is heading"
    )
    assessment_narrative: str = Field(
        description="Narrative about enterprise strengths, weaknesses, state"
    )
    future_narrative: str = Field(
        description="Narrative about enterprise's envisioned future"
    )
    
    # Derived statements
    identity_one_liner: str = Field(
        max_length=140, description="Single-line identity statement"
    )
    purpose_one_liner: str = Field(
        max_length=140, description="Single-line purpose statement"
    )
    
    # Overall consciousness summary
    consciousness_summary: str = Field(
        description="Complete consciousness statement synthesizing all narratives"
    )
    
    # Metadata
    generation_quality: float = Field(
        ge=0.0, le=1.0, description="Quality score of consciousness generation"
    )
    coherence_score: float = Field(
        ge=0.0, le=1.0, description="Internal coherence of statements"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)


class CorporateConsciousness(BaseModel):
    """Complete corporate consciousness - enterprise self-awareness layer"""
    consciousness_id: str
    period: str
    company_name: str
    
    # Core components
    self_model: CorporateSelfModel
    consciousness_statement: ConsciousnessStatement
    
    # Integration sources
    intent_source: Dict[str, float] = Field(
        description="Corporate intent that influenced consciousness"
    )
    agent_sources: List[str] = Field(
        description="Executive agents involved in consciousness formation"
    )
    frontier_status: Dict[str, float] = Field(
        description="Frontier health and optimization metrics"
    )
    culture_attributes: Dict[str, float] = Field(
        description="Cultural attributes that shaped consciousness"
    )
    history_context: str = Field(
        description="Historical context informing consciousness"
    )
    
    # Quality metrics
    authenticity_score: float = Field(
        ge=0.0, le=1.0, description="How authentic consciousness is to enterprise reality"
    )
    clarity_score: float = Field(
        ge=0.0, le=1.0, description="How clear the consciousness articulation is"
    )
    coherence_score: float = Field(
        ge=0.0, le=1.0, description="How coherent components are"
    )
    alignment_score: float = Field(
        ge=0.0, le=1.0, description="How well consciousness aligns with actual operations"
    )
    
    overall_consciousness_score: float = Field(
        ge=0.0, le=1.0, description="Overall consciousness quality"
    )
    
    # Implications
    strategic_implications: List[str] = Field(
        description="Strategic implications of consciousness"
    )
    required_actions: List[str] = Field(
        description="Actions needed to align with consciousness"
    )
    growth_opportunities: List[str] = Field(
        description="Opportunities implied by consciousness"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class ConsciousnessDashboardSummary(BaseModel):
    """Summary of corporate consciousness for dashboard display"""
    consciousness_id: str
    period: str
    
    identity_statement: str
    purpose_statement: str
    strategic_direction: str
    
    current_phase: str
    next_phase: str
    
    overall_score: float
    clarity_score: float
    alignment_score: float
    
    top_strengths: List[str]
    top_challenges: List[str]
    
    strategic_implications: List[str]
    
    consciousness_statement_summary: str
    
    last_updated: datetime
