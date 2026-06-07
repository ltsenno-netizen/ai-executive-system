"""
Narrative Intelligence Engine
=============================

Core engine for narrative intelligence that integrates consciousness,
evolution, intent, agents, frontier, and autonomous loop to generate
context-specific narratives for different audiences.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

from ..models.narrative_intelligence_model import (
    GeneratedNarrative,
    NarrativeAudience,
    NarrativeContext,
    NarrativeStyle,
)
from ..models.corporate_consciousness_evolution_model import ConsciousnessPhase
from ..models.corporate_intent_model import CorporateIntent
from ..models.executive_agent_model import ExecutiveDecisionResult
from ..models.culture_model import CultureProfile
from ..models.external_environment_model_v2 import ExternalEnvironmentState


class NarrativeIntelligenceEngine:
    """Engine for generating intelligent narratives based on corporate context."""

    @staticmethod
    def build_narrative_context(
        audience: NarrativeAudience,
        phase: ConsciousnessPhase,
        intent: CorporateIntent,
        decision: ExecutiveDecisionResult,
        frontier_health: float,
        culture_profile: CultureProfile,
        environment_state: ExternalEnvironmentState,
    ) -> NarrativeContext:
        """
        Build narrative context by integrating all system components.

        Args:
            audience: Target audience for the narrative
            phase: Current consciousness evolution phase
            intent: Current corporate intent
            decision: Latest executive decision result
            frontier_health: Frontier optimization health score
            culture_profile: Current culture profile
            environment_state: Current external environment state

        Returns:
            NarrativeContext: Complete context for narrative generation
        """
        style = NarrativeIntelligenceEngine._select_style(audience)

        return NarrativeContext(
            audience=audience,
            style=style,
            phase=phase,
            intent=intent,
            decision=decision,
            frontier_health=frontier_health,
            culture_profile=culture_profile,
            environment_state=environment_state,
        )

    @staticmethod
    def _select_style(audience: NarrativeAudience) -> NarrativeStyle:
        """
        Select appropriate narrative style based on audience.

        Args:
            audience: Target audience

        Returns:
            NarrativeStyle: Selected style for the audience
        """
        style_mapping = {
            NarrativeAudience.INVESTORS: NarrativeStyle.ANALYTICAL,
            NarrativeAudience.EMPLOYEES: NarrativeStyle.INSPIRATIONAL,
            NarrativeAudience.CUSTOMERS: NarrativeStyle.CONFIDENT,
            NarrativeAudience.PUBLIC: NarrativeStyle.FORMAL,
            NarrativeAudience.PARTNERS: NarrativeStyle.TRANSPARENT,
            NarrativeAudience.CRISIS: NarrativeStyle.TRANSPARENT,
            NarrativeAudience.TRANSFORMATION: NarrativeStyle.CONFIDENT,
            NarrativeAudience.GROWTH: NarrativeStyle.INSPIRATIONAL,
        }

        return style_mapping.get(audience, NarrativeStyle.FORMAL)

    @staticmethod
    def generate_narrative(context: NarrativeContext) -> GeneratedNarrative:
        """
        Generate a narrative based on the provided context.

        Args:
            context: Narrative context with all system integration data

        Returns:
            GeneratedNarrative: Generated narrative with metadata
        """
        text = NarrativeIntelligenceEngine._compose_narrative_text(context)
        key_messages = NarrativeIntelligenceEngine._extract_key_messages(text)
        tone_markers = NarrativeIntelligenceEngine._detect_tone_markers(text)

        return GeneratedNarrative(
            audience=context.audience,
            style=context.style,
            text=text,
            key_messages=key_messages,
            tone_markers=tone_markers,
        )

    @staticmethod
    def _compose_narrative_text(context: NarrativeContext) -> str:
        """
        Compose the narrative text based on context.

        Args:
            context: Narrative context

        Returns:
            str: Composed narrative text
        """
        # Phase-based framing
        phase_framing = NarrativeIntelligenceEngine._get_phase_framing(context.phase)

        # Intent alignment
        intent_section = NarrativeIntelligenceEngine._get_intent_section(context.intent)

        # Executive decision rationale
        decision_section = NarrativeIntelligenceEngine._get_decision_section(context.decision)

        # Frontier health interpretation
        frontier_section = NarrativeIntelligenceEngine._get_frontier_section(context.frontier_health)

        # Culture & environment reflection
        culture_env_section = NarrativeIntelligenceEngine._get_culture_environment_section(
            context.culture_profile, context.environment_state
        )

        # Audience-specific tone and conclusion
        audience_tone = NarrativeIntelligenceEngine._get_audience_tone(context.audience, context.style)

        # Compose final narrative
        narrative_parts = [
            phase_framing,
            intent_section,
            decision_section,
            frontier_section,
            culture_env_section,
            audience_tone,
        ]

        return "\n\n".join(filter(None, narrative_parts))

    @staticmethod
    def _get_phase_framing(phase: ConsciousnessPhase) -> str:
        """Get phase-based narrative framing."""
        phase_framings = {
            ConsciousnessPhase.EMERGING: "We are in the early stages of our journey, discovering our path, learning fast, and building our foundation.",
            ConsciousnessPhase.GROWING: "We are growing rapidly, expanding our capabilities, and strengthening our position through continuous learning.",
            ConsciousnessPhase.CONSOLIDATING: "We are consolidating our gains, refining our operations, and building sustainable excellence.",
            ConsciousnessPhase.TRANSFORMING: "We are undergoing transformation, embracing new paradigms and pioneering innovative approaches.",
            ConsciousnessPhase.MATURING: "We are maturing, demonstrating wisdom, stability, and long-term strategic vision.",
        }
        return phase_framings.get(phase, "We are evolving and adapting to meet the challenges and opportunities ahead.")

    @staticmethod
    def _get_intent_section(intent: CorporateIntent) -> str:
        """Get intent-aligned narrative section."""
        if not intent:
            return ""

        # Use explicit mission/vision/values when available.
        intent_parts = []
        if intent.mission:
            intent_parts.append(f"Our mission is to {intent.mission}.")
        if intent.vision:
            intent_parts.append(f"We envision {intent.vision}.")
        if intent.values:
            values_str = ", ".join(intent.values[:3])
            intent_parts.append(f"We are guided by values such as {values_str}.")

        if intent_parts:
            intent_text = " ".join(intent_parts)
        else:
            priorities = []
            if intent.growth_weight > 0.25:
                priorities.append("growth")
            if intent.profitability_weight > 0.25:
                priorities.append("profitability")
            if intent.innovation_weight > 0.25:
                priorities.append("innovation")
            if intent.stability_weight > 0.25:
                priorities.append("stability")

            if priorities:
                priorities_str = ", ".join(priorities)
                intent_text = f"Our core intent prioritizes {priorities_str} to create sustainable value."
            else:
                intent_text = "Our core intent drives us forward with balanced priorities."

        if intent.cultural_identity:
            intent_text += f" Our cultural identity is {intent.cultural_identity}."

        return intent_text

    @staticmethod
    def _get_decision_section(decision: ExecutiveDecisionResult) -> str:
        """Get executive decision rationale section."""
        if not decision:
            return ""

        if decision.selected_candidate_desc:
            decision_desc = decision.selected_candidate_desc
        elif decision.decision_summary:
            decision_desc = decision.decision_summary
        elif decision.selected_candidate_id:
            decision_desc = f"selected option {decision.selected_candidate_id}"
        else:
            return ""

        return f"Recent executive decisions reflect our strategic direction: {decision_desc}"

    @staticmethod
    def _get_frontier_section(frontier_health: float) -> str:
        """Get frontier health interpretation."""
        if frontier_health >= 0.8:
            return "Our optimization frontier is strong, enabling us to explore new possibilities and maximize value creation."
        elif frontier_health >= 0.6:
            return "We are actively working on frontier optimization, balancing current performance with future potential."
        elif frontier_health >= 0.4:
            return "We are addressing frontier challenges, focusing on improving our strategic positioning."
        else:
            return "We are facing frontier challenges and are focused on improvement to restore strength and competitiveness."

    @staticmethod
    def _get_culture_environment_section(
        culture: CultureProfile,
        environment: ExternalEnvironmentState
    ) -> str:
        """Get culture and environment reflection section."""
        sections = []

        # Culture reflection
        if culture:
            culture_strength = (
                culture.innovation_culture +
                culture.execution_culture +
                culture.stability_culture +
                culture.people_culture
            ) / 4.0
            if culture_strength > 0.7:
                sections.append("Our culture is dynamic and evolving, supporting our ability to adapt and innovate.")
            elif culture_strength > 0.4:
                sections.append("Our culture provides a stable foundation as we navigate changes and opportunities.")
            else:
                sections.append("We are strengthening our cultural foundation to support our strategic objectives.")
        else:
            sections.append("We are strengthening our cultural foundation to support our strategic objectives.")

        # Environment reflection
        if environment:
            highest_shock = 0.0
            if environment.shocks:
                highest_shock = max(shock.severity for shock in environment.shocks)

            if environment.risk_modifier > 0.7 or highest_shock > 0.6:
                sections.append("The external environment presents significant challenges that we are addressing proactively.")
            elif environment.risk_modifier > 0.4 or highest_shock > 0.3:
                sections.append("We are monitoring external developments and adapting our approach accordingly.")
            else:
                sections.append("The current environment provides opportunities for growth and advancement.")
        else:
            sections.append("The current environment provides opportunities for growth and advancement.")

        return " ".join(sections)

    @staticmethod
    def _get_audience_tone(audience: NarrativeAudience, style: NarrativeStyle) -> str:
        """Get audience-specific tone and conclusion."""
        audience_conclusions = {
            NarrativeAudience.INVESTORS: "We remain committed to delivering sustainable value and long-term growth for our stakeholders.",
            NarrativeAudience.EMPLOYEES: "Together, we will continue to build an organization that inspires, challenges, and rewards excellence.",
            NarrativeAudience.CUSTOMERS: "We are dedicated to serving you with excellence and innovation in everything we do.",
            NarrativeAudience.PUBLIC: "We contribute to society through responsible business practices and positive impact.",
            NarrativeAudience.PARTNERS: "We value our partnerships and look forward to continued collaboration and mutual success.",
            NarrativeAudience.CRISIS: "We are taking decisive action to address current challenges and emerge stronger.",
            NarrativeAudience.TRANSFORMATION: "This transformation will position us for greater success and impact.",
            NarrativeAudience.GROWTH: "Our growth journey continues, creating opportunities for all stakeholders.",
        }

        base_conclusion = audience_conclusions.get(audience, "We are committed to our path forward.")

        # Apply style modifiers
        if style == NarrativeStyle.INSPIRATIONAL:
            base_conclusion += " Let's embrace the future with confidence and purpose."
        elif style == NarrativeStyle.ANALYTICAL:
            base_conclusion += " Our data-driven approach ensures sustainable progress."
        elif style == NarrativeStyle.CONFIDENT:
            base_conclusion += " We have the capability and determination to succeed."
        elif style == NarrativeStyle.TRANSPARENT:
            base_conclusion += " We remain committed to open communication and accountability."

        return base_conclusion

    @staticmethod
    def _extract_key_messages(text: str) -> List[str]:
        """Extract key messages from narrative text."""
        # Simple extraction based on sentence structure
        sentences = re.split(r'[.!?]+', text)
        key_messages = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 100:  # Reasonable message length
                # Look for sentences with strong action words or commitments
                if any(word in sentence.lower() for word in [
                    'commit', 'dedicat', 'focus', 'priorit', 'strengthen',
                    'build', 'create', 'deliver', 'achieve', 'pioneer'
                ]):
                    key_messages.append(sentence)

        return key_messages[:5]  # Limit to top 5 messages

    @staticmethod
    def _detect_tone_markers(text: str) -> List[str]:
        """Detect tone markers in narrative text."""
        tone_markers = []

        text_lower = text.lower()

        # Confidence markers
        if any(word in text_lower for word in ['confident', 'strong', 'capable', 'determined', 'committed']):
            tone_markers.append("confident")

        # Inspirational markers
        if any(word in text_lower for word in ['inspire', 'vision', 'purpose', 'together', 'embrace']):
            tone_markers.append("inspirational")

        # Analytical markers
        if any(word in text_lower for word in ['data', 'analysis', 'metrics', 'optimize', 'strategic']):
            tone_markers.append("analytical")

        # Transparent markers
        if any(word in text_lower for word in ['open', 'transparent', 'accountable', 'address', 'proactive']):
            tone_markers.append("transparent")

        # Formal markers
        if any(word in text_lower for word in ['formal', 'professional', 'structured', 'systematic']):
            tone_markers.append("formal")

        return tone_markers

    @staticmethod
    def validate_narrative_context(context: NarrativeContext) -> bool:
        """
        Validate that narrative context has all required components.

        Args:
            context: Narrative context to validate

        Returns:
            bool: True if context is valid
        """
        required_fields = [
            context.audience,
            context.style,
            context.phase,
            context.intent,
            context.decision,
            context.culture_profile,
            context.environment_state,
        ]

        return all(field is not None for field in required_fields) and 0.0 <= context.frontier_health <= 1.0