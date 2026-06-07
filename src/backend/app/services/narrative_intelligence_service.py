"""
Narrative Intelligence Service
==============================

Service layer for narrative intelligence that manages narrative generation,
persistence, retrieval, and export functionality.
"""

import json
from pathlib import Path
from typing import List, Optional

from .narrative_intelligence_engine import NarrativeIntelligenceEngine
from ..models.narrative_intelligence_model import (
    GeneratedNarrative,
    NarrativeAudience,
    NarrativeIntelligenceMetrics,
    NarrativeIntelligenceReport,
)
from .corporate_consciousness_evolution_service import CorporateConsciousnessEvolutionService
from .corporate_intent_service import CorporateIntentService
from .executive_agent_service import ExecutiveAgentService
from .frontier_optimization_service import FrontierOptimizationService
from .culture_service import CultureService
from .external_environment_service import ExternalEnvironmentService


class NarrativeIntelligenceService:
    """Service for managing narrative intelligence operations."""

    # Data directory for narrative persistence
    NARRATIVES_DIR = Path("data/narratives")

    @property
    def NARRATIVES_FILE(self) -> Path:
        """Path to the narrative persistence file."""
        return self.NARRATIVES_DIR / "narratives.json"

    def __init__(self):
        """Initialize the narrative intelligence service."""
        self.engine = NarrativeIntelligenceEngine()
        self._ensure_data_directory()

        # Initialize dependent services (lazy loading to avoid circular imports)
        self._evolution_service = None
        self._intent_service = None
        self._agent_service = None
        self._frontier_service = None
        self._culture_service = None
        self._environment_service = None

    def _ensure_data_directory(self):
        """Ensure the narratives data directory exists."""
        self.NARRATIVES_DIR.mkdir(parents=True, exist_ok=True)
        if not self.NARRATIVES_FILE.exists():
            self._save_narratives([])

    @property
    def evolution_service(self):
        """Lazy load evolution service."""
        if self._evolution_service is None:
            self._evolution_service = CorporateConsciousnessEvolutionService()
        return self._evolution_service

    @property
    def intent_service(self):
        """Lazy load intent service."""
        if self._intent_service is None:
            self._intent_service = CorporateIntentService()
        return self._intent_service

    @property
    def agent_service(self):
        """Lazy load agent service."""
        if self._agent_service is None:
            self._agent_service = ExecutiveAgentService()
        return self._agent_service

    @property
    def frontier_service(self):
        """Lazy load frontier service."""
        if self._frontier_service is None:
            self._frontier_service = FrontierOptimizationService()
        return self._frontier_service

    @property
    def culture_service(self):
        """Lazy load culture service."""
        if self._culture_service is None:
            self._culture_service = CultureService()
        return self._culture_service

    @property
    def environment_service(self):
        """Lazy load environment service."""
        if self._environment_service is None:
            self._environment_service = ExternalEnvironmentService()
        return self._environment_service

    def generate_narrative(self, audience: NarrativeAudience) -> GeneratedNarrative:
        """
        Generate a narrative for the specified audience.

        Args:
            audience: Target audience for the narrative

        Returns:
            GeneratedNarrative: Generated narrative
        """
        # Gather context from all system components
        try:
            evolution_state = self.evolution_service.get_state()
            intent = self.intent_service.get_current_intent()
            decision = self.agent_service.get_latest_decision()
            frontier_health = self.frontier_service.get_health_score()
            culture_profile = self.culture_service.get_current_profile()
            environment_state = self.environment_service.get_current_state()

            # Build narrative context
            context = self.engine.build_narrative_context(
                audience=audience,
                phase=evolution_state.current_phase,
                intent=intent,
                decision=decision,
                frontier_health=frontier_health,
                culture_profile=culture_profile,
                environment_state=environment_state,
            )

            # Generate narrative
            narrative = self.engine.generate_narrative(context)

            # Save narrative
            self._save_narrative(narrative)

            return narrative

        except Exception as e:
            # Graceful degradation - generate basic narrative if services unavailable
            print(f"Warning: Some services unavailable for narrative generation: {e}")
            return self._generate_fallback_narrative(audience)

    def _generate_fallback_narrative(self, audience: NarrativeAudience) -> GeneratedNarrative:
        """Generate a basic fallback narrative when services are unavailable."""
        fallback_text = f"We are committed to our mission and values as we navigate current challenges and opportunities."

        if audience == NarrativeAudience.INVESTORS:
            fallback_text = "We remain focused on delivering sustainable value and long-term growth for our stakeholders."
        elif audience == NarrativeAudience.EMPLOYEES:
            fallback_text = "Together, we will continue to build an organization that inspires and rewards excellence."
        elif audience == NarrativeAudience.CUSTOMERS:
            fallback_text = "We are dedicated to serving you with excellence and innovation."
        elif audience == NarrativeAudience.CRISIS:
            fallback_text = "We are taking decisive action to address current challenges."

        return GeneratedNarrative(
            audience=audience,
            style=NarrativeIntelligenceEngine._select_style(audience),
            text=fallback_text,
            key_messages=["Commitment to excellence", "Focus on stakeholders"],
            tone_markers=["committed", "focused"],
        )

    def get_narrative(self, narrative_id: str) -> Optional[GeneratedNarrative]:
        """
        Retrieve a specific narrative by ID.

        Args:
            narrative_id: Narrative identifier

        Returns:
            GeneratedNarrative or None: The narrative if found
        """
        narratives = self._load_narratives()
        for narrative in narratives:
            if narrative.narrative_id == narrative_id:
                return narrative
        return None

    def get_narrative_history(self, limit: int = 50) -> List[GeneratedNarrative]:
        """
        Get narrative generation history.

        Args:
            limit: Maximum number of narratives to return

        Returns:
            List[GeneratedNarrative]: Recent narratives
        """
        narratives = self._load_narratives()
        # Sort by timestamp (most recent first)
        sorted_narratives = sorted(
            narratives,
            key=lambda x: x.timestamp,
            reverse=True
        )
        return sorted_narratives[:limit]

    def get_narratives_by_audience(
        self,
        audience: NarrativeAudience,
        limit: int = 20
    ) -> List[GeneratedNarrative]:
        """
        Get narratives for a specific audience.

        Args:
            audience: Target audience
            limit: Maximum number of narratives to return

        Returns:
            List[GeneratedNarrative]: Narratives for the audience
        """
        narratives = self._load_narratives()
        audience_narratives = [
            n for n in narratives
            if n.audience == audience
        ]
        # Sort by timestamp (most recent first)
        sorted_narratives = sorted(
            audience_narratives,
            key=lambda x: x.timestamp,
            reverse=True
        )
        return sorted_narratives[:limit]

    def export_narrative_markdown(self, narrative_id: str) -> Optional[str]:
        """
        Export a narrative as markdown.

        Args:
            narrative_id: Narrative identifier

        Returns:
            str or None: Markdown formatted narrative
        """
        narrative = self.get_narrative(narrative_id)
        if not narrative:
            return None

        return self._convert_to_markdown(narrative)

    def _convert_to_markdown(self, narrative: GeneratedNarrative) -> str:
        """Convert narrative to markdown format."""
        markdown = f"""# Narrative for {narrative.audience.value}

**Generated:** {narrative.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
**Style:** {narrative.style.value}

## Narrative Text

{narrative.text}

## Key Messages

{"\\n".join(f"- {msg}" for msg in narrative.key_messages)}

## Tone Markers

{", ".join(narrative.tone_markers)}

---
*Generated by Narrative Intelligence System*
"""

        return markdown

    def get_narrative_metrics(self) -> NarrativeIntelligenceMetrics:
        """
        Get narrative intelligence metrics.

        Returns:
            NarrativeIntelligenceMetrics: Current metrics
        """
        narratives = self._load_narratives()

        if not narratives:
            return NarrativeIntelligenceMetrics()

        # Calculate metrics
        total_narratives = len(narratives)

        audience_distribution = {}
        style_distribution = {}

        for narrative in narratives:
            audience_distribution[narrative.audience.value] = (
                audience_distribution.get(narrative.audience.value, 0) + 1
            )
            style_distribution[narrative.style.value] = (
                style_distribution.get(narrative.style.value, 0) + 1
            )

        # Sort narratives by timestamp
        sorted_narratives = sorted(narratives, key=lambda x: x.timestamp, reverse=True)
        last_generated = sorted_narratives[0].timestamp if sorted_narratives else None

        return NarrativeIntelligenceMetrics(
            total_narratives=total_narratives,
            audience_distribution=audience_distribution,
            style_distribution=style_distribution,
            avg_generation_time=0.0,  # Would need timing data to calculate
            last_generated=last_generated,
        )

    def generate_narrative_report(self, period: str = "last_30_days") -> NarrativeIntelligenceReport:
        """
        Generate a comprehensive narrative intelligence report.

        Args:
            period: Report period

        Returns:
            NarrativeIntelligenceReport: Complete report
        """
        metrics = self.get_narrative_metrics()
        recent_narratives = self.get_narrative_history(limit=10)

        # Calculate audience effectiveness (simplified)
        audience_effectiveness = {}
        for audience in NarrativeAudience:
            audience_narratives = self.get_narratives_by_audience(audience, limit=5)
            if audience_narratives:
                avg_key_messages = sum(len(n.key_messages) for n in audience_narratives) / len(audience_narratives)
                audience_effectiveness[audience.value] = {
                    "count": len(audience_narratives),
                    "avg_key_messages": round(avg_key_messages, 1),
                }

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, audience_effectiveness)

        return NarrativeIntelligenceReport(
            period=period,
            metrics=metrics,
            recent_narratives=recent_narratives,
            audience_effectiveness=audience_effectiveness,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        metrics: NarrativeIntelligenceMetrics,
        audience_effectiveness: dict
    ) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []

        # Check audience coverage
        audiences_with_narratives = set(metrics.audience_distribution.keys())
        all_audiences = {audience.value for audience in NarrativeAudience}

        missing_audiences = all_audiences - audiences_with_narratives
        if missing_audiences:
            recommendations.append(
                f"Generate narratives for missing audiences: {', '.join(missing_audiences)}"
            )

        # Check narrative frequency
        if metrics.total_narratives < 10:
            recommendations.append("Increase narrative generation frequency for better coverage")

        # Check audience balance
        if metrics.audience_distribution:
            max_count = max(metrics.audience_distribution.values())
            min_count = min(metrics.audience_distribution.values())
            if max_count > min_count * 2:
                recommendations.append("Balance narrative generation across different audiences")

        return recommendations

    def _save_narrative(self, narrative: GeneratedNarrative):
        """Save a narrative to persistent storage."""
        narratives = self._load_narratives()
        narratives.append(narrative)
        self._save_narratives(narratives)

    def _load_narratives(self) -> List[GeneratedNarrative]:
        """Load narratives from persistent storage."""
        try:
            with open(self.NARRATIVES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [GeneratedNarrative(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_narratives(self, narratives: List[GeneratedNarrative]):
        """Save narratives to persistent storage."""
        data = [narrative.dict() for narrative in narratives]
        with open(self.NARRATIVES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)