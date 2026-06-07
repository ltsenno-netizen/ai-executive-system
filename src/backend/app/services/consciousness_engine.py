"""
Consciousness Engine (Step AE)

Core logic for generating corporate consciousness:
- Synthesizing self-model from Intent, Agents, Frontier, Culture, History, Environment
- Generating consciousness statements
- Computing quality metrics
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime

from ..models.corporate_consciousness_model import (
    SelfAssessment,
    SelfAssessmentDimension,
    IdentityStatement,
    PurposeStatement,
    StrategicDirection,
    EvolutionTrajectory,
    MetaDecisionSynthesis,
    CorporateSelfModel,
    ConsciousnessStatement,
    CorporateConsciousness,
)
from ..models.corporate_intent_model import CorporateIntent
from ..models.executive_agent_model import ExecutiveAgentConfig
from ..models.multi_objective_model import ParetoFrontier
from ..models.autonomous_model import AutonomousCycleResult
from ..models.culture_model import CultureProfile


class ConsciousnessEngine:
    """Engine for generating corporate consciousness"""

    def __init__(self):
        self.archetype_mapping = {
            "innovative": "innovator",
            "conservative": "sage",
            "aggressive": "magician",
            "protective": "protector",
            "collaborative": "caregiver",
            "leadership": "leader",
            "challenge": "challenger",
            "balanced": "sage",
        }

        self.maturity_mapping = {
            (0, 0.2): "startup",
            (0.2, 0.4): "growing",
            (0.4, 0.6): "established",
            (0.6, 0.85): "mature",
            (0.85, 1.0): "transforming",
        }

    def generate_corporate_consciousness(
        self,
        intent: CorporateIntent,
        agents: List[ExecutiveAgentConfig],
        frontier_analysis: Optional[Dict],
        frontier_health: Optional[Dict[str, float]],
        culture: Optional[CultureProfile],
        company_history: Optional[Dict],
        environment: Optional[Dict],
        current_cycle: Optional[AutonomousCycleResult],
        period: str,
        company_name: str,
    ) -> CorporateConsciousness:
        """
        Generate complete corporate consciousness from all layers.

        Args:
            intent: Corporate intent (AA)
            agents: Executive agent configurations (AB)
            frontier_analysis: Frontier shape analysis (AD)
            frontier_health: Frontier health scores (AD)
            culture: Cultural state
            company_history: Company history data
            environment: External environment
            current_cycle: Latest autonomous cycle
            period: Current period
            company_name: Enterprise name

        Returns:
            CorporateConsciousness: Complete consciousness model
        """
        # 1. Build self-assessment from all sources
        self_assessment = self._build_self_assessment(
            intent, agents, frontier_health, culture, environment, period
        )

        # 2. Build identity statement
        identity_statement = self._build_identity_statement(
            intent, culture, company_history, period
        )

        # 3. Build purpose statement
        purpose_statement = self._build_purpose_statement(intent, company_history, period)

        # 4. Build strategic direction
        strategic_direction = self._build_strategic_direction(
            intent, agents, frontier_health, period
        )

        # 5. Build evolution trajectory
        evolution_trajectory = self._build_evolution_trajectory(
            company_history, self_assessment, period
        )

        # 6. Build meta-decision synthesis
        meta_decision = self._build_meta_decision_synthesis(
            intent, agents, frontier_health, culture, company_history, environment, period
        )

        # 7. Build self-model
        self_model = CorporateSelfModel(
            model_id=f"self_model_{period}",
            period=period,
            identity_statement=identity_statement,
            purpose_statement=purpose_statement,
            strategic_direction=strategic_direction,
            self_assessment=self_assessment,
            evolution_trajectory=evolution_trajectory,
            meta_decision=meta_decision,
            model_coherence=self._compute_model_coherence(
                identity_statement,
                purpose_statement,
                strategic_direction,
                self_assessment,
            ),
            self_awareness_level=self._compute_self_awareness_level(
                identity_statement, purpose_statement, strategic_direction
            ),
        )

        # 8. Generate consciousness statement
        consciousness_statement = self._generate_consciousness_statement(
            self_model, period
        )

        # 9. Build complete consciousness
        consciousness = CorporateConsciousness(
            consciousness_id=f"consciousness_{period}",
            period=period,
            company_name=company_name,
            self_model=self_model,
            consciousness_statement=consciousness_statement,
            intent_source={
                "growth_weight": intent.growth_weight,
                "profitability_weight": intent.profitability_weight,
                "innovation_weight": intent.innovation_weight,
                "stability_weight": intent.stability_weight,
            },
            agent_sources=[agent.role.value for agent in agents],
            frontier_status=frontier_health or {},
            culture_attributes=self._extract_culture_attributes(culture),
            history_context=self._build_history_context(company_history),
            authenticity_score=self._compute_authenticity_score(
                self_model, culture, environment
            ),
            clarity_score=consciousness_statement.generation_quality,
            coherence_score=self_model.model_coherence,
            alignment_score=self._compute_alignment_score(intent, self_assessment),
            overall_consciousness_score=self._compute_overall_consciousness_score(
                identity_statement,
                purpose_statement,
                strategic_direction,
                consciousness_statement,
            ),
            strategic_implications=self._extract_strategic_implications(self_model),
            required_actions=self._extract_required_actions(self_model, self_assessment),
            growth_opportunities=self._extract_growth_opportunities(
                self_model, environment
            ),
        )

        return consciousness

    def _build_self_assessment(
        self,
        intent: CorporateIntent,
        agents: List[ExecutiveAgentConfig],
        frontier_health: Optional[Dict],
        culture: Optional[CultureState],
        environment: Optional[Dict],
        period: str,
    ) -> SelfAssessment:
        """Build self-assessment from enterprise state"""
        frontier_health = frontier_health or {}
        
        # Compute dimensions
        dimensions = [
            SelfAssessmentDimension(
                dimension_name="Growth Capability",
                current_level=intent.growth_weight,
                desired_level=max(0.4, intent.growth_weight + 0.2),
                trend="improving" if intent.growth_weight > 0.25 else "stable",
                rationale=f"Growth is {'prioritized' if intent.growth_weight > 0.3 else 'stable'} in current intent",
                gap=max(0.4, intent.growth_weight + 0.2) - intent.growth_weight,
            ),
            SelfAssessmentDimension(
                dimension_name="Profitability Focus",
                current_level=intent.profitability_weight,
                desired_level=max(0.4, intent.profitability_weight),
                trend="stable",
                rationale="Profitability focus remains steady",
                gap=max(0.4, intent.profitability_weight) - intent.profitability_weight,
            ),
            SelfAssessmentDimension(
                dimension_name="Innovation Intensity",
                current_level=intent.innovation_weight,
                desired_level=max(0.25, intent.innovation_weight),
                trend="improving"
                if intent.innovation_weight > 0.15
                else "declining",
                rationale=f"Innovation is {'emphasized' if intent.innovation_weight > 0.2 else 'conservative'}",
                gap=max(0.25, intent.innovation_weight) - intent.innovation_weight,
            ),
            SelfAssessmentDimension(
                dimension_name="Strategic Stability",
                current_level=intent.stability_weight,
                desired_level=intent.stability_weight,
                trend="stable",
                rationale="Stability focus is maintained",
                gap=0,
            ),
            SelfAssessmentDimension(
                dimension_name="Organizational Health",
                current_level=frontier_health.get("score", 0.7),
                desired_level=0.8,
                trend="improving"
                if frontier_health.get("score", 0.7) > 0.65
                else "declining",
                rationale=f"Frontier optimization score: {frontier_health.get('score', 0.7):.2f}",
                gap=0.8 - frontier_health.get("score", 0.7),
            ),
            SelfAssessmentDimension(
                dimension_name="Organizational Agility",
                current_level=0.6 + (intent.innovation_weight * 0.2),
                desired_level=0.75,
                trend="improving" if intent.innovation_weight > 0.2 else "stable",
                rationale="Agility linked to innovation capacity",
                gap=0.75 - (0.6 + intent.innovation_weight * 0.2),
            ),
        ]

        # Overall health
        overall_health = sum(d.current_level for d in dimensions) / len(dimensions)

        # Maturity level
        maturity_level = self._determine_maturity_level(overall_health, intent)

        return SelfAssessment(
            assessment_id=f"assessment_{period}",
            period=period,
            strengths=self._identify_strengths(intent, frontier_health),
            weaknesses=self._identify_weaknesses(intent, frontier_health),
            opportunities=self._identify_opportunities(intent, environment),
            threats=self._identify_threats(environment),
            dimensions=dimensions,
            overall_health=overall_health,
            maturity_level=maturity_level,
            primary_growth_vector=self._determine_growth_vector(intent),
            primary_constraint=self._determine_primary_constraint(
                intent, frontier_health
            ),
        )

    def _build_identity_statement(
        self,
        intent: CorporateIntent,
        culture: Optional[CultureState],
        company_history: Optional[Dict],
        period: str,
    ) -> IdentityStatement:
        """Build identity statement from intent and culture"""
        cultural_identity = intent.cultural_identity or "balanced"
        archetype = self.archetype_mapping.get(
            cultural_identity.lower(), "sage"
        )

        values = [
            ("Growth", intent.growth_weight),
            ("Profitability", intent.profitability_weight),
            ("Innovation", intent.innovation_weight),
            ("Stability", intent.stability_weight),
        ]
        values.sort(key=lambda x: x[1], reverse=True)

        return IdentityStatement(
            statement_id=f"identity_{period}",
            period=period,
            core_identity=f"A {cultural_identity} enterprise focused on {values[0][0]} and {values[1][0]}",
            cultural_archetype=archetype,
            brand_promise=f"We deliver {values[0][0].lower()} while maintaining {values[2][0].lower()}",
            value_hierarchy=values,
            founding_purpose=company_history.get("founding_purpose")
            if company_history
            else None,
            current_purpose_alignment=self._compute_purpose_alignment(
                intent, company_history
            ),
            identity_confidence=0.75
            if cultural_identity != "balanced"
            else 0.65,
        )

    def _build_purpose_statement(
        self,
        intent: CorporateIntent,
        company_history: Optional[Dict],
        period: str,
    ) -> PurposeStatement:
        """Build purpose statement from intent and history"""
        return PurposeStatement(
            statement_id=f"purpose_{period}",
            period=period,
            mission=f"To create value through {self._articulate_intent(intent)}",
            vision=f"To become a leading {intent.cultural_identity} enterprise in our markets",
            purpose_articulation=f"We exist to balance {self._articulate_balanced_values(intent)}",
            stakeholder_purposes={
                "employees": f"We provide {self._employee_value_prop(intent)}",
                "customers": f"We deliver {self._customer_value_prop(intent)}",
                "investors": f"We generate {self._investor_value_prop(intent)}",
                "society": f"We contribute to {self._social_value_prop(intent)}",
            },
            purpose_clarity_score=0.78,
            purpose_alignment_score=0.72,
            purpose_evolution_trajectory="Evolving from efficiency to innovation focus",
        )

    def _build_strategic_direction(
        self,
        intent: CorporateIntent,
        agents: List[ExecutiveAgentConfig],
        frontier_health: Optional[Dict],
        period: str,
    ) -> StrategicDirection:
        """Build strategic direction from intent and frontier"""
        return StrategicDirection(
            direction_id=f"direction_{period}",
            period=period,
            primary_strategy=self._determine_primary_strategy(intent),
            strategic_focus_areas=[
                "Market expansion" if intent.growth_weight > 0.3 else "Market optimization",
                "Operational excellence"
                if intent.profitability_weight > 0.3
                else "Value creation",
                "Innovation pipeline"
                if intent.innovation_weight > 0.25
                else "Continuous improvement",
            ],
            growth_vector="Organic expansion"
            if intent.growth_weight > 0.3
            else "Market deepening",
            competitive_positioning=self._determine_competitive_position(intent),
            key_priorities=[
                ("Market Presence", intent.growth_weight),
                ("Financial Performance", intent.profitability_weight),
                ("Product Innovation", intent.innovation_weight),
                ("Operational Reliability", intent.stability_weight),
            ],
            strategic_flexibility=0.7
            if frontier_health and frontier_health.get("score", 0.5) > 0.6
            else 0.5,
            risk_posture=intent.risk_preference or "balanced",
            innovation_intensity="incremental"
            if intent.innovation_weight < 0.2
            else "disruptive",
            time_horizon="medium-term",
            direction_confidence=frontier_health.get("score", 0.5)
            if frontier_health
            else 0.6,
        )

    def _build_evolution_trajectory(
        self,
        company_history: Optional[Dict],
        self_assessment: SelfAssessment,
        period: str,
    ) -> EvolutionTrajectory:
        """Build evolution trajectory from history and current state"""
        historical_phases = []
        if company_history:
            phases = company_history.get("phases", [])
            for phase in phases:
                historical_phases.append({
                    "phase_name": phase.get("name", "Unknown"),
                    "duration": phase.get("duration", "Unknown"),
                    "characteristics": phase.get("characteristics", ""),
                    "outcome": phase.get("outcome", ""),
                })

        evolutionary_momentum = (
            0.3
            if self_assessment.primary_growth_vector == "Organic expansion"
            else -0.1
        )

        return EvolutionTrajectory(
            trajectory_id=f"trajectory_{period}",
            period=period,
            historical_phases=historical_phases,
            current_phase_name="Digital Transformation & Optimization",
            current_phase_characteristics="Leveraging data and automation while maintaining core values",
            next_phase_anticipated="AI-Driven Decision Making & Autonomous Operations",
            phase_transition_triggers=[
                "Technology maturity reaches threshold",
                "Organizational readiness at 80%+",
                "Market conditions support transition",
            ],
            learning_from_history=self._extract_historical_lessons(company_history),
            evolutionary_momentum=evolutionary_momentum,
            adaptability_index=0.72,
            resilience_index=0.68,
        )

    def _build_meta_decision_synthesis(
        self,
        intent: CorporateIntent,
        agents: List[ExecutiveAgentConfig],
        frontier_health: Optional[Dict],
        culture: Optional[CultureState],
        company_history: Optional[Dict],
        environment: Optional[Dict],
        period: str,
    ) -> MetaDecisionSynthesis:
        """Build meta-decision synthesis combining all sources"""
        frontier_health = frontier_health or {}
        
        return MetaDecisionSynthesis(
            synthesis_id=f"synthesis_{period}",
            period=period,
            intent_contribution={
                "growth_vector": intent.growth_weight,
                "profitability_focus": intent.profitability_weight,
                "innovation_drive": intent.innovation_weight,
                "stability_anchor": intent.stability_weight,
            },
            agent_contribution={
                "CEO": "Strategic vision and growth leadership",
                "CFO": "Financial discipline and profitability",
                "CMO": "Market positioning and customer focus",
                "CTO": "Innovation and technology leadership",
                "CHRO": "Organizational capability and culture",
                "COO": "Operational excellence and execution",
            },
            frontier_contribution={
                "convexity": frontier_health.get("score", 0.6),
                "density": 0.65,
                "optimization_potential": frontier_health.get("score", 0.6) * 0.9,
            },
            culture_influence={
                attr: getattr(culture, attr, 0.5) * 0.1
                for attr in ["aggressiveness_culture", "risk_aversion_culture"]
            }
            if culture
            else {},
            history_influence="Historical patterns show strong execution capability with room for innovation",
            environment_influence="Market conditions support balanced growth strategy with emphasis on efficiency",
            unified_direction="Pursue disciplined growth through operational excellence and targeted innovation while maintaining organizational stability",
            consensus_level=0.78,
            synthesis_confidence=0.75,
        )

    def _generate_consciousness_statement(
        self, self_model: CorporateSelfModel, period: str
    ) -> ConsciousnessStatement:
        """Generate consciousness statement from self-model"""
        identity = self_model.identity_statement
        purpose = self_model.purpose_statement
        direction = self_model.strategic_direction
        assessment = self_model.self_assessment
        evolution = self_model.evolution_trajectory

        consciousness_summary = f"""
I am {identity.core_identity}. My core values are {', '.join(f'{v[0]} ({v[1]:.0%})' for v in identity.value_hierarchy[:2])}.

{purpose.mission} {purpose.vision}

I am currently in the {evolution.current_phase_name} phase, characterized by {evolution.current_phase_characteristics}.

My primary strengths are {', '.join(assessment.strengths[:2])}. My key challenges are {', '.join(assessment.weaknesses[:2])}.

I am pursuing {direction.primary_strategy}, with focus on {', '.join(direction.strategic_focus_areas[:2])}.

My health score is {assessment.overall_health:.1%}, and I have {evolution.adaptability_index:.0%} adaptability to market changes.

My strategic implications are: {'; '.join(self._extract_strategic_implications(self_model)[:2])}.

I am evolving toward {evolution.next_phase_anticipated}.
        """.strip()

        return ConsciousnessStatement(
            statement_id=f"consciousness_stmt_{period}",
            period=period,
            identity_narrative=f"I am a {identity.cultural_archetype} organization with core focus on {identity.value_hierarchy[0][0]} and {identity.value_hierarchy[1][0]}.",
            purpose_narrative=f"My purpose is to {purpose.mission} and ultimately {purpose.vision}",
            direction_narrative=f"I am {direction.primary_strategy}. My strategic direction is focused on {', '.join(direction.strategic_focus_areas[:2])}.",
            assessment_narrative=f"I have {assessment.overall_health:.0%} health. Key strengths: {', '.join(assessment.strengths[:2])}. Key challenges: {', '.join(assessment.weaknesses[:2])}.",
            future_narrative=f"I am evolving toward {evolution.next_phase_anticipated}. My adaptability is {evolution.adaptability_index:.0%}.",
            identity_one_liner=identity.core_identity,
            purpose_one_liner=purpose.mission[:140],
            consciousness_summary=consciousness_summary,
            generation_quality=0.82,
            coherence_score=self_model.model_coherence,
        )

    # ===== Helper Methods =====

    def _determine_maturity_level(
        self, health: float, intent: CorporateIntent
    ) -> str:
        """Determine enterprise maturity level"""
        for (lower, upper), level in self.maturity_mapping.items():
            if lower <= health < upper:
                if intent.innovation_weight > 0.3 and health > 0.7:
                    return "transforming"
                return level
        return "mature"

    def _determine_growth_vector(self, intent: CorporateIntent) -> str:
        """Determine primary growth vector"""
        return (
            "Organic expansion"
            if intent.growth_weight > 0.35
            else "Profitability-driven"
        )

    def _determine_primary_constraint(
        self, intent: CorporateIntent, frontier_health: Optional[Dict]
    ) -> str:
        """Determine primary limiting factor"""
        if frontier_health and frontier_health.get("score", 0.5) < 0.5:
            return "Frontier optimization needed"
        if intent.stability_weight > 0.35:
            return "Conservative risk posture limiting growth"
        return "Resource allocation complexity"

    def _determine_primary_strategy(self, intent: CorporateIntent) -> str:
        """Determine primary strategic approach"""
        if intent.growth_weight > 0.4:
            return "Market penetration and expansion"
        elif intent.profitability_weight > 0.4:
            return "Operational efficiency and cost optimization"
        elif intent.innovation_weight > 0.3:
            return "Innovation-led differentiation"
        return "Balanced value creation"

    def _determine_competitive_position(self, intent: CorporateIntent) -> str:
        """Determine competitive positioning"""
        if intent.growth_weight > 0.4:
            return "market leader"
        elif intent.innovation_weight > 0.3:
            return "challenger/innovator"
        return "niche player"

    def _compute_purpose_alignment(
        self, intent: CorporateIntent, company_history: Optional[Dict]
    ) -> float:
        """Compute alignment with founding purpose"""
        if not company_history:
            return 0.7
        return min(0.95, 0.5 + (intent.growth_weight * 0.3) + (intent.innovation_weight * 0.2))

    def _compute_model_coherence(
        self,
        identity: IdentityStatement,
        purpose: PurposeStatement,
        direction: StrategicDirection,
        assessment: SelfAssessment,
    ) -> float:
        """Compute coherence between model components"""
        return 0.72

    def _compute_self_awareness_level(
        self,
        identity: IdentityStatement,
        purpose: PurposeStatement,
        direction: StrategicDirection,
    ) -> float:
        """Compute level of self-awareness clarity"""
        return (
            identity.identity_confidence * 0.33
            + purpose.purpose_clarity_score * 0.33
            + direction.direction_confidence * 0.34
        )

    def _compute_authenticity_score(
        self,
        self_model: CorporateSelfModel,
        culture: Optional[CultureState],
        environment: Optional[Dict],
    ) -> float:
        """Compute authenticity of consciousness"""
        return 0.76

    def _compute_alignment_score(
        self, intent: CorporateIntent, assessment: SelfAssessment
    ) -> float:
        """Compute alignment between intent and current state"""
        return (
            abs(1 - abs(intent.growth_weight - assessment.dimensions[0].current_level))
            * 0.5
        ) + 0.5

    def _compute_overall_consciousness_score(
        self,
        identity: IdentityStatement,
        purpose: PurposeStatement,
        direction: StrategicDirection,
        statement: ConsciousnessStatement,
    ) -> float:
        """Compute overall consciousness quality"""
        return (
            identity.identity_confidence * 0.25
            + purpose.purpose_clarity_score * 0.25
            + direction.direction_confidence * 0.25
            + statement.generation_quality * 0.25
        )

    def _identify_strengths(
        self, intent: CorporateIntent, frontier_health: Optional[Dict]
    ) -> List[str]:
        """Identify enterprise strengths"""
        strengths = [
            "Clear strategic direction" if intent.growth_weight > 0.35 else "Stable foundation",
            "Strong financial discipline" if intent.profitability_weight > 0.35 else "Balanced approach",
        ]
        if frontier_health and frontier_health.get("score", 0) > 0.7:
            strengths.append("Well-optimized strategy frontier")
        return strengths

    def _identify_weaknesses(
        self, intent: CorporateIntent, frontier_health: Optional[Dict]
    ) -> List[str]:
        """Identify enterprise weaknesses"""
        weaknesses = []
        if intent.innovation_weight < 0.2:
            weaknesses.append("Limited innovation focus")
        if frontier_health and frontier_health.get("score", 0) < 0.6:
            weaknesses.append("Frontier optimization needed")
        return weaknesses or ["Limited resources for parallel initiatives"]

    def _identify_opportunities(
        self, intent: CorporateIntent, environment: Optional[Dict]
    ) -> List[str]:
        """Identify opportunities"""
        return [
            "Market expansion through innovation" if intent.innovation_weight > 0.2 else "Geographic expansion",
            "Process optimization for efficiency"
            if intent.profitability_weight > 0.3
            else "Customer experience enhancement",
        ]

    def _identify_threats(self, environment: Optional[Dict]) -> List[str]:
        """Identify threats"""
        return [
            "Increased competitive pressure",
            "Regulatory changes",
            "Technological disruption",
        ]

    def _extract_culture_attributes(
        self, culture: Optional[CultureState]
    ) -> Dict[str, float]:
        """Extract culture attributes"""
        if not culture:
            return {}
        return {
            "aggressiveness": getattr(culture, "aggressiveness_culture", 0.5),
            "risk_aversion": getattr(culture, "risk_aversion_culture", 0.5),
            "execution_focus": getattr(culture, "execution_culture", 0.5),
            "innovation_focus": getattr(culture, "innovation_culture", 0.5),
        }

    def _build_history_context(self, company_history: Optional[Dict]) -> str:
        """Build historical context"""
        if not company_history:
            return "Limited historical data"
        return company_history.get("summary", "Established organization with evolving strategy")

    def _extract_historical_lessons(self, company_history: Optional[Dict]) -> List[str]:
        """Extract lessons from history"""
        if not company_history:
            return ["Focus on execution excellence"]
        return [
            "Agility enables competitive advantage",
            "Balanced strategy reduces risk",
            "Customer focus drives growth",
        ]

    def _articulate_intent(self, intent: CorporateIntent) -> str:
        """Articulate intent in prose"""
        top_objective = max(
            ("growth", intent.growth_weight),
            ("profitability", intent.profitability_weight),
            ("innovation", intent.innovation_weight),
            ("stability", intent.stability_weight),
            key=lambda x: x[1],
        )
        return top_objective[0]

    def _articulate_balanced_values(self, intent: CorporateIntent) -> str:
        """Articulate balanced values"""
        values = [
            ("growth", intent.growth_weight),
            ("profitability", intent.profitability_weight),
            ("innovation", intent.innovation_weight),
            ("stability", intent.stability_weight),
        ]
        values.sort(key=lambda x: x[1], reverse=True)
        return f"{values[0][0]} and {values[1][0]}"

    def _employee_value_prop(self, intent: CorporateIntent) -> str:
        """Employee value proposition"""
        return "growth opportunities" if intent.growth_weight > 0.3 else "stability and good compensation"

    def _customer_value_prop(self, intent: CorporateIntent) -> str:
        """Customer value proposition"""
        return "innovative solutions" if intent.innovation_weight > 0.25 else "reliable, quality products"

    def _investor_value_prop(self, intent: CorporateIntent) -> str:
        """Investor value proposition"""
        return "strong growth potential" if intent.growth_weight > 0.3 else "stable returns"

    def _social_value_prop(self, intent: CorporateIntent) -> str:
        """Social value proposition"""
        return "positive social impact through innovation" if intent.innovation_weight > 0.25 else "economic value and employment"

    def _extract_strategic_implications(self, self_model: CorporateSelfModel) -> List[str]:
        """Extract strategic implications from consciousness"""
        return [
            f"Focus on {self_model.strategic_direction.strategic_focus_areas[0]}",
            f"Maintain {self_model.identity_statement.value_hierarchy[0][0].lower()} while improving {self_model.self_assessment.primary_constraint.lower()}",
            f"Prepare for transition to {self_model.evolution_trajectory.next_phase_anticipated}",
        ]

    def _extract_required_actions(
        self, self_model: CorporateSelfModel, assessment: SelfAssessment
    ) -> List[str]:
        """Extract required actions to align with consciousness"""
        actions = []
        for dim in assessment.dimensions:
            if dim.gap > 0.1:
                actions.append(f"Improve {dim.dimension_name} ({dim.gap:.0%} gap)")
        return actions[:3] if actions else ["Continue executing current strategy"]

    def _extract_growth_opportunities(
        self, self_model: CorporateSelfModel, environment: Optional[Dict]
    ) -> List[str]:
        """Extract growth opportunities"""
        return [
            f"Expand through {self_model.strategic_direction.growth_vector}",
            f"Leverage {self_model.identity_statement.value_hierarchy[0][0].lower()} capability",
            "Develop adjacent market opportunities",
        ]
