from typing import Dict, List, Optional
import random
from datetime import datetime

from src.backend.app.models.enterprise_evolution_model import EnterpriseEvolutionResult
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.external_environment_model_v2 import ExternalEnvironmentState

class EnterpriseEvolutionEngine:
    """Engine for computing enterprise evolution based on culture, environment, and leadership feedback loops."""

    def __init__(self):
        self.feedback_weights = {
            'environment_to_culture': 0.3,
            'culture_to_leadership': 0.4,
            'leadership_to_environment': 0.3
        }

    def compute_enterprise_evolution(
        self,
        culture: CultureProfile,
        environment: ExternalEnvironmentState,
        leadership: ExecutiveTeam,
        period: str
    ) -> EnterpriseEvolutionResult:
        """
        Compute enterprise evolution by analyzing feedback loops between
        culture, external environment, and leadership.
        """
        # Calculate shifts between components
        environment_to_culture_shift = self._calculate_environment_to_culture_shift(environment, culture)
        culture_to_leadership_shift = self._calculate_culture_to_leadership_shift(culture, leadership)
        leadership_to_environment_shift = self._calculate_leadership_to_environment_shift(leadership, environment)

        # Calculate overall evolution score
        evolution_score = self._calculate_evolution_score(
            environment_to_culture_shift,
            culture_to_leadership_shift,
            leadership_to_environment_shift
        )

        # Identify active feedback loops
        feedback_loops = self._identify_feedback_loops(
            environment_to_culture_shift,
            culture_to_leadership_shift,
            leadership_to_environment_shift
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            evolution_score,
            environment_to_culture_shift,
            culture_to_leadership_shift,
            leadership_to_environment_shift
        )

        return EnterpriseEvolutionResult(
            period=period,
            evolution_score=evolution_score,
            culture_shift=culture_to_leadership_shift,
            environment_shift=environment_to_culture_shift,
            leadership_shift=leadership_to_environment_shift,
            feedback_loops=feedback_loops,
            recommendations=recommendations
        )

    def _calculate_environment_to_culture_shift(
        self,
        environment: ExternalEnvironmentState,
        culture: CultureProfile
    ) -> Dict[str, float]:
        """Calculate how external environment influences culture."""
        shifts = {}

        # Economic pressure affects innovation culture
        economic_pressure = getattr(environment, 'economic_pressure', 0.5)
        shifts['innovation'] = economic_pressure * 0.2 - 0.1

        # Market volatility affects risk tolerance
        market_volatility = getattr(environment, 'market_volatility', 0.5)
        shifts['risk_tolerance'] = market_volatility * -0.15

        # Competitive intensity affects collaboration
        competitive_intensity = getattr(environment, 'competitive_intensity', 0.5)
        shifts['collaboration'] = competitive_intensity * -0.1

        return shifts

    def _calculate_culture_to_leadership_shift(
        self,
        culture: CultureProfile,
        leadership: ExecutiveTeam
    ) -> Dict[str, float]:
        """Calculate how culture influences leadership development."""
        shifts = {}

        # Innovation culture affects leadership innovation
        innovation = getattr(culture, 'innovation_culture', 0.5)
        shifts['innovation_focus'] = innovation * 0.25

        # Risk tolerance affects leadership risk appetite
        risk_tolerance = getattr(culture, 'risk_aversion_culture', 0.5)
        shifts['risk_appetite'] = (1 - risk_tolerance) * 0.3  # Invert since risk_aversion is opposite

        # Collaboration affects leadership team dynamics
        collaboration = getattr(culture, 'people_culture', 0.5)
        shifts['team_cohesion'] = collaboration * 0.2

        return shifts

    def _calculate_leadership_to_environment_shift(
        self,
        leadership: ExecutiveTeam,
        environment: ExternalEnvironmentState
    ) -> Dict[str, float]:
        """Calculate how leadership influences environment adaptation."""
        shifts = {}

        # Leadership innovation affects market positioning
        innovation_focus = getattr(leadership, 'innovation_focus', 0.5)
        shifts['market_positioning'] = innovation_focus * 0.15

        # Risk appetite affects competitive strategy
        risk_appetite = getattr(leadership, 'risk_appetite', 0.5)
        shifts['competitive_strategy'] = risk_appetite * 0.2

        # Team cohesion affects stakeholder relationships
        team_cohesion = getattr(leadership, 'team_cohesion', 0.5)
        shifts['stakeholder_relations'] = team_cohesion * 0.1

        return shifts

    def _calculate_evolution_score(
        self,
        env_to_culture: Dict[str, float],
        culture_to_leadership: Dict[str, float],
        leadership_to_env: Dict[str, float]
    ) -> float:
        """Calculate overall evolution score based on feedback loop strength."""
        # Base score from component interactions
        base_score = 50.0

        # Add weighted contributions from each shift
        env_contribution = sum(env_to_culture.values()) * 10
        culture_contribution = sum(culture_to_leadership.values()) * 15
        leadership_contribution = sum(leadership_to_env.values()) * 10

        total_score = base_score + env_contribution + culture_contribution + leadership_contribution

        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, total_score))

    def _identify_feedback_loops(
        self,
        env_to_culture: Dict[str, float],
        culture_to_leadership: Dict[str, float],
        leadership_to_env: Dict[str, float]
    ) -> Dict[str, List[str]]:
        """Identify active feedback loops in the system."""
        loops = {
            'positive': [],
            'negative': [],
            'neutral': []
        }

        # Check for reinforcing loops
        if env_to_culture.get('innovation', 0) > 0.1 and culture_to_leadership.get('innovation_focus', 0) > 0.1:
            loops['positive'].append('Innovation reinforcement loop')

        if culture_to_leadership.get('risk_appetite', 0) < -0.1 and leadership_to_env.get('competitive_strategy', 0) < -0.1:
            loops['negative'].append('Risk aversion cycle')

        if leadership_to_env.get('stakeholder_relations', 0) > 0.1:
            loops['positive'].append('Stakeholder relationship improvement')

        return loops

    def _generate_recommendations(
        self,
        evolution_score: float,
        env_to_culture: Dict[str, float],
        culture_to_leadership: Dict[str, float],
        leadership_to_env: Dict[str, float]
    ) -> List[str]:
        """Generate evolution recommendations based on analysis."""
        recommendations = []

        if evolution_score < 40:
            recommendations.append("Strengthen feedback loops between culture and leadership")
            recommendations.append("Review external environment adaptation strategies")

        if evolution_score > 80:
            recommendations.append("Monitor for potential over-adaptation to current environment")
            recommendations.append("Consider proactive culture evolution initiatives")

        # Specific recommendations based on shifts
        if env_to_culture.get('innovation', 0) < 0:
            recommendations.append("Address external pressures inhibiting innovation culture")

        if culture_to_leadership.get('team_cohesion', 0) < 0:
            recommendations.append("Improve leadership team collaboration and cohesion")

        return recommendations