"""
Multi-Company Comparative Service (Step AK)

Orchestrates profile building and comparison report generation.
Persists comparison reports for retrieval.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from ..models.multi_company_comparative_model import (
    CompanyId,
    CompanyProfile,
    MultiCompanyComparisonReport,
)
from .multi_company_comparative_engine import MultiCompanyComparativeEngine


class MultiCompanyComparativeService:
    """Service for multi-company comparative intelligence."""

    def __init__(self):
        self.engine = MultiCompanyComparativeEngine()
        self.storage_dir = os.path.join(
            os.path.dirname(__file__), '../../../data/multi_company_comparisons'
        )
        os.makedirs(self.storage_dir, exist_ok=True)
        self.last_report: Optional[MultiCompanyComparisonReport] = None

    @staticmethod
    def build_company_profile(
        company_id: str,
        company_name: str,
        consciousness_clarity: float = 0.5,
        evolution_phase: str = "INTENTIONAL",
        evolution_speed: float = 0.5,
        frontier_health: float = 0.6,
        frontier_score: float = 60.0,
        culture_profile: Optional[Dict[str, float]] = None,
        risk_posture: float = 0.5,
        narrative_consistency: float = 0.65,
        narrative_clarity: float = 0.65,
        meta_cognition_score: float = 0.6,
        scenario_resilience: Optional[Dict[str, float]] = None,
        learning_agility: float = 0.65,
    ) -> CompanyProfile:
        """Build a company profile for comparison."""
        return CompanyProfile(
            company=CompanyId(company_id=company_id, name=company_name),
            consciousness_clarity=consciousness_clarity,
            evolution_phase=evolution_phase,
            evolution_speed=evolution_speed,
            frontier_health=frontier_health,
            frontier_score=frontier_score,
            culture_profile=culture_profile or {
                "innovation": 0.5,
                "execution": 0.5,
                "risk_aversion": 0.5,
                "brand": 0.5,
                "cost": 0.5,
                "people": 0.5,
                "stability": 0.5,
            },
            risk_posture=risk_posture,
            narrative_consistency=narrative_consistency,
            narrative_clarity=narrative_clarity,
            meta_cognition_score=meta_cognition_score,
            scenario_resilience=scenario_resilience or {
                "BASELINE": 0.6,
                "RECESSION": 0.5,
                "TECH_BOOM": 0.7,
                "OPTIMISTIC": 0.75,
                "PESSIMISTIC": 0.45,
            },
            learning_agility=learning_agility,
        )

    def compare_companies(
        self,
        company_ids: List[CompanyId],
        profiles: Optional[List[CompanyProfile]] = None,
    ) -> MultiCompanyComparisonReport:
        """
        Generate a comprehensive comparison report.

        Args:
            company_ids: List of companies to compare
            profiles: Optional pre-built profiles. If None, will use build_company_profile.

        Returns:
            MultiCompanyComparisonReport
        """
        if profiles is None:
            # Build default profiles if not provided
            profiles = [
                self.build_company_profile(cid.company_id, cid.name)
                for cid in company_ids
            ]

        # Add profiles to engine
        for profile in profiles:
            self.engine.add_profile(profile)

        # Build and return report
        report = self.engine.build_comparison_report(company_ids, profiles)

        # Cache and persist
        self.last_report = report
        self._save_report(report)

        return report

    def get_last_comparison(self) -> Optional[MultiCompanyComparisonReport]:
        """Get the most recent comparison report."""
        if self.last_report:
            return self.last_report

        # Try to load from disk
        latest_file = self._get_latest_report_file()
        if latest_file:
            return self._load_report(latest_file)

        return None

    def get_report_by_id(self, report_id: str) -> Optional[MultiCompanyComparisonReport]:
        """Retrieve a specific comparison report by ID."""
        file_path = os.path.join(self.storage_dir, f"{report_id}.json")
        if not os.path.exists(file_path):
            return None
        return self._load_report(file_path)

    def list_available_companies(self) -> List[CompanyId]:
        """List all available companies (self + known competitors)."""
        # For now, return standard company set
        # In production, would query a company registry
        return [
            CompanyId(company_id="self", name="Our Company"),
            CompanyId(company_id="competitor_a", name="Competitor A"),
            CompanyId(company_id="competitor_b", name="Competitor B"),
            CompanyId(company_id="competitor_c", name="Competitor C"),
        ]

    def _save_report(self, report: MultiCompanyComparisonReport) -> None:
        """Persist comparison report to JSON."""
        file_path = os.path.join(self.storage_dir, f"{report.report_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2, ensure_ascii=False, default=str)

    def _load_report(self, file_path: str) -> Optional[MultiCompanyComparisonReport]:
        """Load comparison report from JSON."""
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        try:
            return MultiCompanyComparisonReport(**data)
        except Exception:
            return None

    def _get_latest_report_file(self) -> Optional[str]:
        """Get the most recently modified report file."""
        if not os.path.exists(self.storage_dir):
            return None

        files = [
            os.path.join(self.storage_dir, f)
            for f in os.listdir(self.storage_dir)
            if f.endswith(".json")
        ]

        if not files:
            return None

        return max(files, key=os.path.getmtime)

    def generate_markdown_report(self, report: MultiCompanyComparisonReport) -> str:
        """Generate a markdown-formatted version of the comparison report."""
        lines = [
            "# Multi-Company Comparative Intelligence Report",
            "",
            f"**Generated:** {report.comparison_date.isoformat()}",
            "",
            f"**Report ID:** `{report.report_id}`",
            "",
            "## Companies Compared",
            "",
        ]

        for company in report.companies:
            lines.append(f"- **{company.name}** (`{company.company_id}`)")

        lines.extend([
            "",
            "## Executive Summary",
            "",
            report.narrative_summary,
            "",
            "## Comparative Metrics",
            "",
        ])

        # Group metrics by category
        categories = {}
        for metric in report.metrics:
            if metric.category not in categories:
                categories[metric.category] = []
            categories[metric.category].append(metric)

        for category in sorted(categories.keys()):
            lines.append(f"### {category.title()}")
            lines.append("")

            for metric in categories[category]:
                lines.append(f"**{metric.name}**")
                lines.append("")
                lines.append(f"_{metric.description}_")
                lines.append("")

                # Metric values table
                lines.append("| Company | Score |")
                lines.append("|---------|-------|")
                for company_id in sorted(metric.values.keys()):
                    value = metric.values[company_id]
                    lines.append(f"| {company_id} | {value:.2f} |")

                if metric.best_company_id:
                    lines.append(
                        f"- **Best:** {metric.best_company_id} ({metric.best_value:.2f})"
                    )
                if metric.worst_company_id:
                    lines.append(
                        f"- **Worst:** {metric.worst_company_id} ({metric.worst_value:.2f})"
                    )
                if metric.average_value is not None:
                    lines.append(f"- **Average:** {metric.average_value:.2f}")

                lines.append("")

        # Clusters
        lines.extend([
            "## Company Archetypes",
            "",
        ])

        for cluster in report.clusters:
            lines.append(f"### {cluster.cluster_name}")
            lines.append("")
            lines.append(f"_{cluster.description}_")
            lines.append("")
            lines.append("**Companies in this cluster:**")
            for cid in cluster.company_ids:
                lines.append(f"- {cid}")
            lines.append("")

        # Dimensions
        lines.extend([
            "## Dimension Analysis",
            "",
        ])

        for dimension in report.dimensions:
            lines.append(f"### {dimension.dimension}")
            lines.append("")
            lines.append(dimension.summary)
            lines.append("")

            if dimension.key_differences:
                lines.append("**Key Differences:**")
                for diff in dimension.key_differences[:3]:
                    lines.append(f"- {diff}")
                lines.append("")

        # Strategic implications
        if report.strategic_implications:
            lines.extend([
                "## Strategic Implications",
                "",
            ])

            for implication in report.strategic_implications:
                lines.append(f"- {implication}")

            lines.append("")

        return "\n".join(lines)
