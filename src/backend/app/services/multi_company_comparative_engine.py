"""
Multi-Company Comparative Analysis Engine (Step AK)

Analyzes and compares multiple company profiles across multiple dimensions.
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid
import statistics

from ..models.multi_company_comparative_model import (
    CompanyId,
    CompanyProfile,
    ComparativeMetric,
    CompanyCluster,
    ComparisonDimension,
    MultiCompanyComparisonReport,
)


class MultiCompanyComparativeEngine:
    """Engine for multi-company comparative intelligence."""

    def __init__(self):
        self.profiles: Dict[str, CompanyProfile] = {}

    def add_profile(self, profile: CompanyProfile) -> None:
        """Register a company profile."""
        self.profiles[profile.company.company_id] = profile

    def compute_comparative_metrics(self, profiles: List[CompanyProfile]) -> List[ComparativeMetric]:
        """Compute all comparative metrics across profiles."""
        metrics = []

        # Category: Consciousness
        metrics.append(self._compute_consciousness_clarity(profiles))

        # Category: Evolution
        metrics.append(self._compute_evolution_speed(profiles))

        # Category: Frontier
        metrics.append(self._compute_frontier_health(profiles))
        metrics.append(self._compute_frontier_score(profiles))

        # Category: Culture
        metrics.append(self._compute_risk_posture(profiles))

        # Category: Narrative
        metrics.append(self._compute_narrative_consistency(profiles))
        metrics.append(self._compute_narrative_clarity(profiles))

        # Category: Meta-Cognition
        metrics.append(self._compute_meta_cognition(profiles))

        # Category: Scenario
        metrics.extend(self._compute_scenario_resilience(profiles))

        # Learning agility
        metrics.append(self._compute_learning_agility(profiles))

        return metrics

    def _compute_consciousness_clarity(self, profiles: List[CompanyProfile]) -> ComparativeMetric:
        """Clarity of corporate consciousness."""
        values = {p.company.company_id: p.consciousness_clarity for p in profiles}
        return self._build_metric(
            metric_id="consciousness_clarity",
            name="Consciousness Clarity",
            category="consciousness",
            description="How clearly the company understands its own identity and purpose (0-1)",
            values=values,
            unit="score"
        )

    def _compute_evolution_speed(self, profiles: List[CompanyProfile]) -> ComparativeMetric:
        """Speed of consciousness evolution."""
        values = {p.company.company_id: p.evolution_speed for p in profiles}
        return self._build_metric(
            metric_id="evolution_speed",
            name="Evolution Speed",
            category="evolution",
            description="Rate at which the company transitions through consciousness phases (0-1)",
            values=values,
            unit="transitions/period"
        )

    def _compute_frontier_health(self, profiles: List[CompanyProfile]) -> ComparativeMetric:
        """Strategic frontier health."""
        values = {p.company.company_id: p.frontier_health for p in profiles}
        return self._build_metric(
            metric_id="frontier_health",
            name="Frontier Health",
            category="frontier",
            description="Overall health of strategic frontier (0-1)",
            values=values,
            unit="score"
        )

    def _compute_frontier_score(self, profiles: List[CompanyProfile]) -> ComparativeMetric:
        """Frontier analysis score."""
        values = {p.company.company_id: p.frontier_score for p in profiles}
        return self._build_metric(
            metric_id="frontier_score",
            name="Frontier Score",
            category="frontier",
            description="Comprehensive frontier health score (0-100)",
            values=values,
            unit="points"
        )

    def _compute_risk_posture(self, profiles: List[CompanyProfile]) -> ComparativeMetric:
        """Risk tolerance vs stability orientation."""
        values = {p.company.company_id: p.risk_posture for p in profiles}
        return self._build_metric(
            metric_id="risk_posture",
            name="Risk Posture",
            category="culture",
            description="Tendency toward risk-taking vs stability (0=stable, 1=aggressive)",
            values=values,
            unit="posture"
        )

    def _compute_narrative_consistency(self, profiles: List[CompanyProfile]) -> ComparativeMetric:
        """Consistency of narrative themes."""
        values = {p.company.company_id: p.narrative_consistency for p in profiles}
        return self._build_metric(
            metric_id="narrative_consistency",
            name="Narrative Consistency",
            category="narrative",
            description="How consistently the company's narrative reinforces its identity (0-1)",
            values=values,
            unit="score"
        )

    def _compute_narrative_clarity(self, profiles: List[CompanyProfile]) -> ComparativeMetric:
        """Clarity of corporate narrative."""
        values = {p.company.company_id: p.narrative_clarity for p in profiles}
        return self._build_metric(
            metric_id="narrative_clarity",
            name="Narrative Clarity",
            category="narrative",
            description="How clear and coherent the company's narrative is (0-1)",
            values=values,
            unit="score"
        )

    def _compute_meta_cognition(self, profiles: List[CompanyProfile]) -> ComparativeMetric:
        """Meta-cognition maturity."""
        values = {p.company.company_id: p.meta_cognition_score for p in profiles}
        return self._build_metric(
            metric_id="meta_cognition",
            name="Meta-Cognition Maturity",
            category="meta_cognition",
            description="Self-awareness of patterns, blindspots, and limitations (0-1)",
            values=values,
            unit="score"
        )

    def _compute_scenario_resilience(self, profiles: List[CompanyProfile]) -> List[ComparativeMetric]:
        """Resilience across different scenarios."""
        metrics = []
        
        # Get all scenario types from profiles
        all_scenarios = set()
        for profile in profiles:
            all_scenarios.update(profile.scenario_resilience.keys())

        for scenario in sorted(all_scenarios):
            values = {
                p.company.company_id: p.scenario_resilience.get(scenario, 0.5)
                for p in profiles
            }
            metrics.append(self._build_metric(
                metric_id=f"scenario_resilience_{scenario.lower()}",
                name=f"Resilience to {scenario}",
                category="scenario",
                description=f"Resilience when facing {scenario} scenario (0-1)",
                values=values,
                unit="resilience"
            ))

        return metrics

    def _compute_learning_agility(self, profiles: List[CompanyProfile]) -> ComparativeMetric:
        """Learning agility across companies."""
        values = {p.company.company_id: p.learning_agility for p in profiles}
        return self._build_metric(
            metric_id="learning_agility",
            name="Learning Agility",
            category="meta_cognition",
            description="Capacity to learn from experience and adapt (0-1)",
            values=values,
            unit="score"
        )

    def _build_metric(
        self,
        metric_id: str,
        name: str,
        category: str,
        description: str,
        values: Dict[str, float],
        unit: Optional[str] = None
    ) -> ComparativeMetric:
        """Build a comparative metric with computed statistics."""
        best_company = max(values, key=values.get) if values else None
        worst_company = min(values, key=values.get) if values else None
        
        return ComparativeMetric(
            metric_id=metric_id,
            name=name,
            category=category,
            description=description,
            values=values,
            unit=unit,
            best_company_id=best_company,
            worst_company_id=worst_company,
            best_value=max(values.values()) if values else None,
            worst_value=min(values.values()) if values else None,
            average_value=statistics.mean(values.values()) if values else None,
        )

    def cluster_companies(self, profiles: List[CompanyProfile]) -> List[CompanyCluster]:
        """Classify companies into archetypes."""
        clusters = []

        # Aggressive Innovator: high risk_posture, high frontier_health, high learning_agility
        aggressive_innovators = [
            p for p in profiles
            if p.risk_posture > 0.65 and p.frontier_health > 0.6 and p.learning_agility > 0.6
        ]
        if aggressive_innovators:
            clusters.append(CompanyCluster(
                cluster_id="aggressive_innovator",
                cluster_name="Aggressive Innovator",
                description="High risk tolerance, strong frontier exploration, rapid learning",
                company_ids=[p.company.company_id for p in aggressive_innovators],
                defining_traits={
                    "risk_posture": 0.75,
                    "frontier_health": 0.70,
                    "learning_agility": 0.70,
                }
            ))

        # Stable Operator: low risk_posture, moderate frontier_health, consistent narrative
        stable_operators = [
            p for p in profiles
            if p.risk_posture < 0.40 and p.frontier_health < 0.65 and p.narrative_consistency > 0.7
        ]
        if stable_operators:
            clusters.append(CompanyCluster(
                cluster_id="stable_operator",
                cluster_name="Stable Operator",
                description="Low risk tolerance, steady operations, high narrative consistency",
                company_ids=[p.company.company_id for p in stable_operators],
                defining_traits={
                    "risk_posture": 0.25,
                    "frontier_health": 0.50,
                    "narrative_consistency": 0.80,
                }
            ))

        # Transformational: high evolution_speed, high consciousness_clarity, moderate risk
        transformational = [
            p for p in profiles
            if p.evolution_speed > 0.65 and p.consciousness_clarity > 0.65 and 0.35 < p.risk_posture < 0.65
        ]
        if transformational:
            clusters.append(CompanyCluster(
                cluster_id="transformational",
                cluster_name="Transformational",
                description="Rapid consciousness evolution, clear identity, balanced risk approach",
                company_ids=[p.company.company_id for p in transformational],
                defining_traits={
                    "evolution_speed": 0.75,
                    "consciousness_clarity": 0.75,
                    "risk_posture": 0.50,
                }
            ))

        # Awakening: high meta_cognition, improving consciousness, learning agility
        awakening = [
            p for p in profiles
            if p.meta_cognition_score > 0.7 and p.learning_agility > 0.65 and p.consciousness_clarity > 0.55
        ]
        if awakening:
            clusters.append(CompanyCluster(
                cluster_id="awakening",
                cluster_name="Awakening",
                description="High self-awareness, strong learning capacity, evolving consciousness",
                company_ids=[p.company.company_id for p in awakening],
                defining_traits={
                    "meta_cognition_score": 0.80,
                    "learning_agility": 0.75,
                    "consciousness_clarity": 0.65,
                }
            ))

        # Struggling: low across most metrics
        all_clustered = set()
        for cluster in clusters:
            all_clustered.update(cluster.company_ids)
        
        struggling = [p for p in profiles if p.company.company_id not in all_clustered]
        if struggling:
            clusters.append(CompanyCluster(
                cluster_id="struggling",
                cluster_name="Struggling",
                description="Lower performance across key dimensions, needs development",
                company_ids=[p.company.company_id for p in struggling],
                defining_traits={
                    "frontier_health": 0.40,
                    "consciousness_clarity": 0.40,
                    "meta_cognition_score": 0.45,
                }
            ))

        return clusters

    def build_dimension_analyses(
        self,
        profiles: List[CompanyProfile],
        metrics: List[ComparativeMetric]
    ) -> List[ComparisonDimension]:
        """Build high-level dimension summaries."""
        dimensions = []

        # Consciousness Dimension
        consciousness_metrics = [m for m in metrics if m.category == "consciousness"]
        dimensions.append(ComparisonDimension(
            dimension="Consciousness",
            summary=self._summarize_dimension_metrics(consciousness_metrics),
            key_differences=[
                f"{m.best_company_id} leads in {m.name} ({m.best_value:.2f})"
                for m in consciousness_metrics if m.best_company_id
            ],
            leading_companies=[m.best_company_id for m in consciousness_metrics if m.best_company_id]
        ))

        # Evolution Dimension
        evolution_metrics = [m for m in metrics if m.category == "evolution"]
        dimensions.append(ComparisonDimension(
            dimension="Evolution",
            summary=self._summarize_dimension_metrics(evolution_metrics),
            key_differences=[
                f"{m.best_company_id} leads in {m.name} ({m.best_value:.2f})"
                for m in evolution_metrics if m.best_company_id
            ],
            leading_companies=[m.best_company_id for m in evolution_metrics if m.best_company_id]
        ))

        # Frontier Dimension
        frontier_metrics = [m for m in metrics if m.category == "frontier"]
        dimensions.append(ComparisonDimension(
            dimension="Frontier",
            summary=self._summarize_dimension_metrics(frontier_metrics),
            key_differences=[
                f"{m.best_company_id} excels in {m.name} ({m.best_value:.2f})"
                for m in frontier_metrics if m.best_company_id
            ],
            leading_companies=[m.best_company_id for m in frontier_metrics if m.best_company_id]
        ))

        # Culture Dimension
        culture_metrics = [m for m in metrics if m.category == "culture"]
        dimensions.append(ComparisonDimension(
            dimension="Culture",
            summary=self._summarize_dimension_metrics(culture_metrics),
            key_differences=[
                f"{m.best_company_id} shows stronger {m.name} ({m.best_value:.2f})"
                for m in culture_metrics if m.best_company_id
            ],
            leading_companies=[m.best_company_id for m in culture_metrics if m.best_company_id]
        ))

        # Narrative Dimension
        narrative_metrics = [m for m in metrics if m.category == "narrative"]
        dimensions.append(ComparisonDimension(
            dimension="Narrative",
            summary=self._summarize_dimension_metrics(narrative_metrics),
            key_differences=[
                f"{m.best_company_id} has superior {m.name} ({m.best_value:.2f})"
                for m in narrative_metrics if m.best_company_id
            ],
            leading_companies=[m.best_company_id for m in narrative_metrics if m.best_company_id]
        ))

        # Meta-Cognition Dimension
        meta_metrics = [m for m in metrics if m.category == "meta_cognition"]
        dimensions.append(ComparisonDimension(
            dimension="Meta-Cognition",
            summary=self._summarize_dimension_metrics(meta_metrics),
            key_differences=[
                f"{m.best_company_id} demonstrates higher {m.name} ({m.best_value:.2f})"
                for m in meta_metrics if m.best_company_id
            ],
            leading_companies=[m.best_company_id for m in meta_metrics if m.best_company_id]
        ))

        # Scenario Resilience Dimension
        scenario_metrics = [m for m in metrics if m.category == "scenario"]
        dimensions.append(ComparisonDimension(
            dimension="Scenario Resilience",
            summary=self._summarize_dimension_metrics(scenario_metrics),
            key_differences=[
                f"{m.best_company_id} is most resilient to {m.name} ({m.best_value:.2f})"
                for m in scenario_metrics if m.best_company_id
            ],
            leading_companies=[m.best_company_id for m in scenario_metrics if m.best_company_id]
        ))

        return dimensions

    def _summarize_dimension_metrics(self, metrics: List[ComparativeMetric]) -> str:
        """Generate a summary of metrics in a dimension."""
        if not metrics:
            return "No data available for this dimension."
        
        best_performers = set()
        for m in metrics:
            if m.best_company_id:
                best_performers.add(m.best_company_id)
        
        if best_performers:
            return f"Key performers: {', '.join(sorted(best_performers))}. Average across all: {metrics[0].average_value:.2f}"
        return f"Dimension averages: {metrics[0].average_value:.2f}"

    def build_comparison_report(
        self,
        company_ids: List[CompanyId],
        profiles: List[CompanyProfile]
    ) -> MultiCompanyComparisonReport:
        """Build complete comparison report."""
        metrics = self.compute_comparative_metrics(profiles)
        clusters = self.cluster_companies(profiles)
        dimensions = self.build_dimension_analyses(profiles, metrics)

        # Generate narrative summary
        narrative = self._generate_narrative_summary(company_ids, profiles, metrics, clusters, dimensions)

        # Generate strategic implications
        implications = self._generate_strategic_implications(metrics, clusters, dimensions)

        return MultiCompanyComparisonReport(
            report_id=str(uuid.uuid4()),
            companies=company_ids,
            comparison_date=datetime.now(),
            metrics=metrics,
            clusters=clusters,
            dimensions=dimensions,
            narrative_summary=narrative,
            strategic_implications=implications,
        )

    def _generate_narrative_summary(
        self,
        company_ids: List[CompanyId],
        profiles: List[CompanyProfile],
        metrics: List[ComparativeMetric],
        clusters: List[CompanyCluster],
        dimensions: List[ComparisonDimension]
    ) -> str:
        """Generate executive narrative summary."""
        company_names = [c.name for c in company_ids]
        
        top_performers = {}
        for m in metrics:
            if m.best_company_id:
                top_performers[m.best_company_id] = top_performers.get(m.best_company_id, 0) + 1

        lines = [
            f"Comparative analysis of {', '.join(company_names)}.",
            "",
            "Key Findings:",
            f"- {len(clusters)} distinct archetypes identified: {', '.join([c.cluster_name for c in clusters])}.",
            f"- Most frequent leader: {max(top_performers, key=top_performers.get) if top_performers else 'No clear leader'}.",
            f"- Leadership concentrated across {len(top_performers)} companies.",
            "",
            "Dimension Highlights:",
        ]

        for dim in dimensions[:3]:
            if dim.leading_companies:
                lines.append(f"- {dim.dimension}: Led by {', '.join(set(dim.leading_companies[:2]))}.")

        return "\n".join(lines)

    def _generate_strategic_implications(
        self,
        metrics: List[ComparativeMetric],
        clusters: List[CompanyCluster],
        dimensions: List[ComparisonDimension]
    ) -> List[str]:
        """Generate strategic implications from comparison."""
        implications = []

        # Find gap leaders
        frontier_metrics = [m for m in metrics if m.category == "frontier"]
        if frontier_metrics:
            implications.append(
                f"Frontier leaders show {frontier_metrics[0].best_value - frontier_metrics[0].worst_value:.2f} "
                "point advantage in strategic positioning."
            )

        # Cluster diversity
        if len(clusters) > 2:
            implications.append(
                f"Heterogeneous landscape: {len(clusters)} distinct archetypes suggest different strategies are viable."
            )

        # Evolution rate
        evolution_metrics = [m for m in metrics if m.category == "evolution"]
        if evolution_metrics and evolution_metrics[0].best_value > 0.7:
            implications.append(
                f"Fast-evolving companies ({evolution_metrics[0].best_value:.2f}) are setting pace; others risk falling behind."
            )

        # Meta-cognition gap
        meta_metrics = [m for m in metrics if m.category == "meta_cognition"]
        if meta_metrics and meta_metrics[0].best_value - meta_metrics[0].worst_value > 0.3:
            implications.append(
                "Significant self-awareness gap: Leaders understand their blindspots; laggards may be unaware of vulnerabilities."
            )

        return implications
