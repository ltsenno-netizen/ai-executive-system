"""
Multi-Company Comparative Intelligence Model (Step AK)

Enables comparison and analysis of multiple company personalities
across consciousness, evolution, culture, narrative, and meta-cognition dimensions.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field

from .corporate_consciousness_evolution_model import ConsciousnessEvolutionState
from .culture_model import CultureProfile
from .meta_cognition_model import MetaCognitionReport


class CompanyId(BaseModel):
    """Company identifier."""
    company_id: str = Field(..., description="Unique company identifier")
    name: str = Field(..., description="Human-readable company name")


class CompanyProfile(BaseModel):
    """Complete profile of a company for comparison."""
    company: CompanyId
    consciousness_clarity: float = Field(
        ..., ge=0.0, le=1.0,
        description="Clarity of corporate consciousness (0-1)"
    )
    evolution_phase: str = Field(
        ...,
        description="Current consciousness evolution phase (e.g., 'REACTIVE', 'INTENTIONAL', 'EMERGENT')"
    )
    evolution_speed: float = Field(
        ..., ge=0.0, le=1.0,
        description="Speed of phase transitions (0-1)"
    )
    frontier_health: float = Field(
        ..., ge=0.0, le=1.0,
        description="Strategic frontier health score (0-1)"
    )
    frontier_score: float = Field(
        ..., ge=0.0, le=100.0,
        description="Frontier analysis score (0-100)"
    )
    culture_profile: Dict[str, float] = Field(
        default_factory=dict,
        description="Culture dimensions (innovation, execution, risk_aversion, etc.)"
    )
    risk_posture: float = Field(
        ..., ge=0.0, le=1.0,
        description="Risk appetite vs stability (0=stable, 1=aggressive)"
    )
    narrative_consistency: float = Field(
        ..., ge=0.0, le=1.0,
        description="Consistency of narrative themes (0-1)"
    )
    narrative_clarity: float = Field(
        ..., ge=0.0, le=1.0,
        description="Clarity/coherence of corporate narrative (0-1)"
    )
    meta_cognition_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Meta-cognition maturity (self-awareness of patterns, blindspots)"
    )
    scenario_resilience: Dict[str, float] = Field(
        default_factory=dict,
        description="Resilience scores by scenario type (e.g., 'RECESSION': 0.72)"
    )
    learning_agility: float = Field(
        ..., ge=0.0, le=1.0,
        description="Capacity to learn and adapt (0-1)"
    )
    timestamp: datetime = Field(default_factory=datetime.now)


class ComparativeMetric(BaseModel):
    """Single comparative metric across multiple companies."""
    metric_id: str = Field(..., description="Unique metric identifier")
    name: str = Field(..., description="Human-readable metric name")
    category: str = Field(
        ...,
        description="Category (consciousness, evolution, frontier, culture, narrative, meta_cognition, scenario)"
    )
    description: str = Field(..., description="Detailed description of what the metric measures")
    values: Dict[str, float] = Field(
        ...,
        description="Company ID → metric value mapping"
    )
    unit: Optional[str] = Field(None, description="Unit of measurement if applicable")
    best_company_id: Optional[str] = Field(None, description="Company ID with highest value")
    worst_company_id: Optional[str] = Field(None, description="Company ID with lowest value")
    best_value: Optional[float] = Field(None, description="Best (highest) value")
    worst_value: Optional[float] = Field(None, description="Worst (lowest) value")
    average_value: Optional[float] = Field(None, description="Average across all companies")


class CompanyCluster(BaseModel):
    """Cluster of companies with similar characteristics."""
    cluster_id: str = Field(..., description="Cluster identifier")
    cluster_name: str = Field(..., description="Human-readable cluster name (e.g., 'AGGRESSIVE_INNOVATOR')")
    description: str = Field(..., description="Characteristics of this cluster")
    company_ids: List[str] = Field(default_factory=list, description="Company IDs in this cluster")
    defining_traits: Dict[str, float] = Field(
        default_factory=dict,
        description="Key traits that define this cluster"
    )


class ComparisonDimension(BaseModel):
    """High-level dimension analysis in the comparison."""
    dimension: str = Field(
        ...,
        description="Dimension name (consciousness, evolution, culture, frontier, narrative, meta_cognition, scenario)"
    )
    summary: str = Field(..., description="Summary of findings on this dimension")
    key_differences: List[str] = Field(
        default_factory=list,
        description="Notable differences between companies on this dimension"
    )
    leading_companies: List[str] = Field(
        default_factory=list,
        description="Company IDs leading on this dimension"
    )


class MultiCompanyComparisonReport(BaseModel):
    """Comprehensive multi-company comparison report."""
    report_id: str = Field(..., description="Unique report identifier (UUID)")
    companies: List[CompanyId] = Field(..., description="Companies included in comparison")
    comparison_date: datetime = Field(
        default_factory=datetime.now,
        description="When this comparison was generated"
    )
    
    # Core analytics
    metrics: List[ComparativeMetric] = Field(
        default_factory=list,
        description="List of comparative metrics"
    )
    clusters: List[CompanyCluster] = Field(
        default_factory=list,
        description="Company clusters/archetypes"
    )
    dimensions: List[ComparisonDimension] = Field(
        default_factory=list,
        description="High-level dimension summaries"
    )
    
    # Narrative insights
    narrative_summary: str = Field(
        ...,
        description="Executive summary of comparative insights"
    )
    strategic_implications: List[str] = Field(
        default_factory=list,
        description="Strategic insights from the comparison"
    )
    recommendation: Optional[str] = Field(
        None,
        description="Actionable recommendation based on comparison"
    )


class MultiCompanyComparisonSummary(BaseModel):
    """Dashboard-friendly summary of multi-company comparison."""
    companies: List[str] = Field(..., description="Company names in comparison")
    strongest_company: Optional[str] = Field(None, description="Company with highest overall score")
    weakest_company: Optional[str] = Field(None, description="Company with lowest overall score")
    cluster_count: int = Field(0, description="Number of distinct clusters identified")
    cluster_labels: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Cluster name → [company_ids]"
    )
    key_insight: str = Field(..., description="Single most important finding")
    last_compared: datetime = Field(default_factory=datetime.now)
