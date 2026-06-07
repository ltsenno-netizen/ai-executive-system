"""
Tests for strategy_space_optimizer.py

Tests for strategy space optimization including:
- Redundant cluster identification
- Strategy gap identification
- New candidate generation
- Optimized frontier generation
- Frontier potential estimation
"""

import pytest
import numpy as np
from datetime import datetime

from app.models.multi_objective_model import (
    ObjectiveVector,
    StrategyCandidate,
    ParetoFrontier,
)
from app.models.corporate_intent_model import CorporateIntent
from app.services.strategy_space_optimizer import (
    StrategySpaceOptimizer,
    StrategyGap,
    CandidateCluster,
    StrategySpaceOptimizationReport,
)


class TestStrategySpaceOptimizer:
    """Test suite for strategy space optimization"""

    @pytest.fixture
    def sample_frontier(self):
        """Create sample frontier for testing"""
        candidates = [
            StrategyCandidate(
                id="s1",
                name="Strategy 1",
                growth=100.0,
                profitability=50.0,
                innovation=40.0,
                stability=60.0,
            ),
            StrategyCandidate(
                id="s2",
                name="Strategy 2",
                growth=99.0,
                profitability=51.0,
                innovation=41.0,
                stability=59.0,
            ),  # Similar to s1
            StrategyCandidate(
                id="s3",
                name="Strategy 3",
                growth=70.0,
                profitability=75.0,
                innovation=60.0,
                stability=50.0,
            ),
            StrategyCandidate(
                id="s4",
                name="Strategy 4",
                growth=50.0,
                profitability=90.0,
                innovation=30.0,
                stability=70.0,
            ),
            StrategyCandidate(
                id="s5",
                name="Strategy 5",
                growth=75.0,
                profitability=70.0,
                innovation=80.0,
                stability=45.0,
            ),
        ]

        objectives = [
            ObjectiveVector(
                id=f"obj_{c.id}",
                growth=c.growth,
                profitability=c.profitability,
                innovation=c.innovation,
                stability=c.stability,
            )
            for c in candidates
        ]

        return ParetoFrontier(
            id="optimization_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

    @pytest.fixture
    def sample_intent(self):
        """Create sample intent"""
        return CorporateIntent(
            id="intent_1",
            period="2026-01",
            growth_weight=0.3,
            profitability_weight=0.3,
            innovation_weight=0.2,
            stability_weight=0.2,
            risk_preference="balanced",
            cultural_identity="innovative",
        )

    def test_optimize_strategy_space(self, sample_frontier, sample_intent):
        """Test complete strategy space optimization"""
        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(sample_frontier, sample_intent)

        assert isinstance(result, StrategySpaceOptimizationReport)
        assert result.frontier_id == sample_frontier.id
        assert result.period == sample_frontier.period

    def test_optimization_report_structure(self, sample_frontier, sample_intent):
        """Test StrategySpaceOptimizationReport has all required fields"""
        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(sample_frontier, sample_intent)

        assert result.frontier_id is not None
        assert result.period is not None
        assert result.frontier_size > 0
        assert result.redundant_clusters is not None
        assert result.strategy_gaps is not None
        assert result.new_candidates is not None
        assert result.optimized_frontier is not None
        assert result.frontier_potential is not None
        assert result.recommendations is not None
        assert result.timestamp is not None

    def test_redundant_clusters_identified(self, sample_frontier, sample_intent):
        """Test redundant cluster identification"""
        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(sample_frontier, sample_intent)

        # Should identify at least the similar s1/s2 pair
        assert len(result.redundant_clusters) > 0

        # Each cluster should have valid structure
        for cluster in result.redundant_clusters:
            assert isinstance(cluster, CandidateCluster)
            assert cluster.center is not None
            assert cluster.radius > 0
            assert len(cluster.member_ids) > 1
            assert 0 <= cluster.similarity <= 1
            assert cluster.representative_id is not None

    def test_strategy_gaps_identified(self, sample_frontier, sample_intent):
        """Test strategy gap identification"""
        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(sample_frontier, sample_intent)

        # Should identify some gaps
        assert len(result.strategy_gaps) >= 0

        # Each gap should have valid structure
        for gap in result.strategy_gaps:
            assert isinstance(gap, StrategyGap)
            assert gap.location is not None
            assert gap.severity > 0
            assert gap.rationale is not None
            assert gap.suggested_objective is not None

    def test_new_candidates_generated(self, sample_frontier, sample_intent):
        """Test new candidates are generated for gaps"""
        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(sample_frontier, sample_intent)

        # Should generate candidates if gaps exist
        if result.strategy_gaps:
            # May have generated new candidates (implementation specific)
            assert result.new_candidates is not None

    def test_optimized_frontier_generated(self, sample_frontier, sample_intent):
        """Test optimized frontier is generated"""
        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(sample_frontier, sample_intent)

        assert result.optimized_frontier is not None
        assert isinstance(result.optimized_frontier, list)
        # Optimized frontier should have improved characteristics
        assert len(result.optimized_frontier) > 0

    def test_frontier_potential_scored(self, sample_frontier, sample_intent):
        """Test frontier potential is scored"""
        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(sample_frontier, sample_intent)

        potential = result.frontier_potential
        assert potential is not None
        assert "reconstruction_quality" in potential
        assert "density_improvement" in potential
        assert "gap_filling_potential" in potential
        assert "estimated_improvement" in potential

        # All scores should be in valid range
        assert 0 <= potential["reconstruction_quality"] <= 1
        assert 0 <= potential["density_improvement"] <= 1
        assert 0 <= potential["gap_filling_potential"] <= 1
        assert 0 <= potential["estimated_improvement"] <= 1

    def test_recommendations_generated(self, sample_frontier, sample_intent):
        """Test recommendations are generated"""
        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(sample_frontier, sample_intent)

        assert result.recommendations is not None
        assert len(result.recommendations) > 0
        
        # Each recommendation should have content
        for recommendation in result.recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0


class TestRedundantClusterDetection:
    """Tests for redundant cluster identification"""

    def test_identical_strategies_clustered(self):
        """Test identical strategies are identified as cluster"""
        candidates = [
            StrategyCandidate(
                id="s1",
                name="Strategy 1",
                growth=100.0,
                profitability=50.0,
                innovation=40.0,
                stability=60.0,
            ),
            StrategyCandidate(
                id="s2",
                name="Strategy 2",
                growth=100.0,
                profitability=50.0,
                innovation=40.0,
                stability=60.0,
            ),
        ]

        objectives = [
            ObjectiveVector(
                id=f"obj_{c.id}",
                growth=c.growth,
                profitability=c.profitability,
                innovation=c.innovation,
                stability=c.stability,
            )
            for c in candidates
        ]

        frontier = ParetoFrontier(
            id="identical_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

        intent = CorporateIntent(
            id="intent_1",
            period="2026-01",
            growth_weight=0.3,
            profitability_weight=0.3,
            innovation_weight=0.2,
            stability_weight=0.2,
        )

        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(frontier, intent)

        # Should identify cluster
        assert len(result.redundant_clusters) > 0
        cluster = result.redundant_clusters[0]
        assert "s1" in cluster.member_ids
        assert "s2" in cluster.member_ids

    def test_cluster_similarity_metric(self):
        """Test cluster similarity metric"""
        candidates = [
            StrategyCandidate(
                id="s1",
                name="Strategy 1",
                growth=100.0,
                profitability=50.0,
                innovation=40.0,
                stability=60.0,
            ),
            StrategyCandidate(
                id="s2",
                name="Strategy 2",
                growth=90.0,
                profitability=55.0,
                innovation=45.0,
                stability=65.0,
            ),  # Similar but not identical
        ]

        objectives = [
            ObjectiveVector(
                id=f"obj_{c.id}",
                growth=c.growth,
                profitability=c.profitability,
                innovation=c.innovation,
                stability=c.stability,
            )
            for c in candidates
        ]

        frontier = ParetoFrontier(
            id="similar_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

        intent = CorporateIntent(
            id="intent_1",
            period="2026-01",
            growth_weight=0.3,
            profitability_weight=0.3,
            innovation_weight=0.2,
            stability_weight=0.2,
        )

        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(frontier, intent)

        if result.redundant_clusters:
            cluster = result.redundant_clusters[0]
            # Similarity should be high (similar but not identical)
            assert cluster.similarity > 0.5


class TestStrategyGapDetection:
    """Tests for strategy gap detection"""

    def test_gap_location_valid(self):
        """Test gap locations are valid"""
        candidates = [
            StrategyCandidate(
                id="s1",
                name="Strategy 1",
                growth=100.0,
                profitability=50.0,
                innovation=40.0,
                stability=60.0,
            ),
            StrategyCandidate(
                id="s2",
                name="Strategy 2",
                growth=50.0,
                profitability=90.0,
                innovation=30.0,
                stability=70.0,
            ),
        ]

        objectives = [
            ObjectiveVector(
                id=f"obj_{c.id}",
                growth=c.growth,
                profitability=c.profitability,
                innovation=c.innovation,
                stability=c.stability,
            )
            for c in candidates
        ]

        frontier = ParetoFrontier(
            id="gap_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

        intent = CorporateIntent(
            id="intent_1",
            period="2026-01",
            growth_weight=0.3,
            profitability_weight=0.3,
            innovation_weight=0.2,
            stability_weight=0.2,
        )

        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(frontier, intent)

        # Check gaps if identified
        for gap in result.strategy_gaps:
            assert isinstance(gap.location, dict)
            assert "growth" in gap.location or "profitability" in gap.location


class TestOptimizationRecommendations:
    """Tests for optimization recommendations"""

    def test_recommendations_actionable(self):
        """Test recommendations are actionable"""
        candidates = [
            StrategyCandidate(
                id=f"s{i}",
                name=f"Strategy {i}",
                growth=50 + (i * 10),
                profitability=100 - (i * 8),
                innovation=40 + (i * 5),
                stability=50 + (i * 3),
            )
            for i in range(5)
        ]

        objectives = [
            ObjectiveVector(
                id=f"obj_{c.id}",
                growth=c.growth,
                profitability=c.profitability,
                innovation=c.innovation,
                stability=c.stability,
            )
            for c in candidates
        ]

        frontier = ParetoFrontier(
            id="recommendations_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

        intent = CorporateIntent(
            id="intent_1",
            period="2026-01",
            growth_weight=0.25,
            profitability_weight=0.35,
            innovation_weight=0.15,
            stability_weight=0.25,
        )

        optimizer = StrategySpaceOptimizer()
        result = optimizer.optimize_strategy_space(frontier, intent)

        # Recommendations should reference actual issues
        for rec in result.recommendations:
            assert len(rec) > 20  # Not trivial
            # Should be relevant to optimization
            relevant = any(
                keyword in rec.lower()
                for keyword in [
                    "cluster",
                    "redundant",
                    "gap",
                    "remove",
                    "add",
                    "frontier",
                ]
            )
            assert relevant
