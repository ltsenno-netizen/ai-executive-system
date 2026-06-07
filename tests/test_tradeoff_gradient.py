"""
Tests for tradeoff_gradient.py

Tests for gradient computation and analysis including:
- Local gradient estimation
- Tradeoff profile computation
- Frontier quality scoring
- Actionable insights extraction
"""

import pytest
import numpy as np
from datetime import datetime

from app.models.multi_objective_model import (
    ObjectiveVector,
    StrategyCandidate,
    ParetoFrontier,
)
from app.services.tradeoff_gradient import (
    TradeoffGradientEngine,
    TradeoffGradient,
    TradeoffProfile,
    FrontierGradientReport,
)


class TestTradeoffGradientEngine:
    """Test suite for tradeoff gradient computation"""

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
                growth=85.0,
                profitability=65.0,
                innovation=50.0,
                stability=55.0,
            ),
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
                growth=55.0,
                profitability=85.0,
                innovation=45.0,
                stability=65.0,
            ),
            StrategyCandidate(
                id="s5",
                name="Strategy 5",
                growth=75.0,
                profitability=70.0,
                innovation=75.0,
                stability=50.0,
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
            id="gradient_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

    def test_compute_tradeoff_gradients(self, sample_frontier):
        """Test complete gradient computation"""
        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(sample_frontier)

        assert isinstance(result, FrontierGradientReport)
        assert result.frontier_id == sample_frontier.id
        assert result.frontier_size == len(sample_frontier.objectives)

    def test_gradient_report_structure(self, sample_frontier):
        """Test FrontierGradientReport has all required fields"""
        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(sample_frontier)

        assert result.frontier_id is not None
        assert result.period is not None
        assert result.frontier_size > 0
        assert result.key_gradients is not None
        assert result.all_gradients is not None
        assert result.dominant_tradeoff is not None
        assert result.neutral_pairs is not None
        assert result.quality_scores is not None
        assert result.actionable_insights is not None
        assert result.timestamp is not None

    def test_key_gradients_extracted(self, sample_frontier):
        """Test that key gradients are extracted"""
        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(sample_frontier)

        # Should identify some key gradients
        assert len(result.key_gradients) > 0

        # Each gradient should have required fields
        for gradient in result.key_gradients:
            assert isinstance(gradient, TradeoffGradient)
            assert gradient.source_objective is not None
            assert gradient.target_objective is not None
            assert gradient.magnitude > 0
            assert gradient.interpretation is not None

    def test_dominant_tradeoff_identified(self, sample_frontier):
        """Test dominant tradeoff identification"""
        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(sample_frontier)

        assert result.dominant_tradeoff is not None
        assert isinstance(result.dominant_tradeoff, dict)
        assert "source" in result.dominant_tradeoff
        assert "target" in result.dominant_tradeoff
        assert "magnitude" in result.dominant_tradeoff

    def test_quality_scores_valid_range(self, sample_frontier):
        """Test quality scores are in valid range"""
        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(sample_frontier)

        quality = result.quality_scores
        assert 0 <= quality.get("tradeoff_diversity", 0) <= 1
        assert 0 <= quality.get("gradient_stability", 0) <= 1
        assert 0 <= quality.get("gradient_balance", 0) <= 1
        assert 0 <= quality.get("objective_independence", 0) <= 1

    def test_actionable_insights_generated(self, sample_frontier):
        """Test actionable insights are generated"""
        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(sample_frontier)

        assert len(result.actionable_insights) > 0
        
        # Each insight should have content
        for insight in result.actionable_insights:
            assert isinstance(insight, str)
            assert len(insight) > 0

    def test_neutral_pairs_identified(self, sample_frontier):
        """Test neutral objective pairs identification"""
        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(sample_frontier)

        # Neutral pairs are optional but if present should be tuples
        for pair in result.neutral_pairs:
            assert isinstance(pair, tuple)
            assert len(pair) == 2

    def test_all_gradients_coverage(self, sample_frontier):
        """Test all possible gradients are computed"""
        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(sample_frontier)

        # Should have gradients between different objectives
        assert len(result.all_gradients) > 0

        objectives = ["growth", "profitability", "innovation", "stability"]
        
        # Verify gradient structure
        for gradient in result.all_gradients:
            assert gradient.source_objective in objectives
            assert gradient.target_objective in objectives
            assert gradient.source_objective != gradient.target_objective
            assert gradient.magnitude > 0

    def test_gradient_magnitude_positive(self, sample_frontier):
        """Test gradient magnitudes are positive"""
        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(sample_frontier)

        for gradient in result.all_gradients:
            assert gradient.magnitude > 0

    def test_gradient_interpretation_present(self, sample_frontier):
        """Test gradient interpretations are present"""
        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(sample_frontier)

        for gradient in result.all_gradients:
            assert gradient.interpretation is not None
            assert isinstance(gradient.interpretation, str)
            assert len(gradient.interpretation) > 0


class TestGradientQualityMetrics:
    """Tests for gradient quality metric computation"""

    def test_tradeoff_diversity_score(self):
        """Test tradeoff diversity metric"""
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
                growth=80.0,
                profitability=70.0,
                innovation=50.0,
                stability=50.0,
            ),
            StrategyCandidate(
                id="s3",
                name="Strategy 3",
                growth=60.0,
                profitability=80.0,
                innovation=60.0,
                stability=40.0,
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
            id="diversity_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(frontier)

        diversity = result.quality_scores.get("tradeoff_diversity", 0)
        assert 0 <= diversity <= 1

    def test_gradient_stability_score(self):
        """Test gradient stability metric"""
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
            id="stability_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(frontier)

        stability = result.quality_scores.get("gradient_stability", 0)
        assert 0 <= stability <= 1


class TestTradeoffProfileGeneration:
    """Tests for tradeoff profile generation"""

    def test_profile_has_required_fields(self):
        """Test TradeoffProfile has all required fields"""
        profile = TradeoffProfile(
            source_objective="growth",
            target_objective="stability",
            local_gradients=[0.5, 0.6, 0.55],
            average_gradient=0.55,
            min_gradient=0.5,
            max_gradient=0.6,
            gradient_stability=0.95,
        )

        assert profile.source_objective == "growth"
        assert profile.target_objective == "stability"
        assert len(profile.local_gradients) == 3
        assert profile.average_gradient > 0
        assert profile.min_gradient > 0
        assert profile.max_gradient > 0
        assert 0 <= profile.gradient_stability <= 1

    def test_gradient_object_structure(self):
        """Test TradeoffGradient object structure"""
        gradient = TradeoffGradient(
            source_objective="growth",
            target_objective="profitability",
            magnitude=0.75,
            interpretation="Moderate tradeoff: 1% growth gain costs 0.75% profitability",
        )

        assert gradient.source_objective == "growth"
        assert gradient.target_objective == "profitability"
        assert gradient.magnitude > 0
        assert len(gradient.interpretation) > 0


class TestActionableInsights:
    """Tests for actionable insights generation"""

    def test_insights_are_human_readable(self):
        """Test generated insights are human-readable"""
        candidates = [
            StrategyCandidate(
                id="s1",
                name="Strategy 1",
                growth=100.0,
                profitability=40.0,
                innovation=50.0,
                stability=50.0,
            ),
            StrategyCandidate(
                id="s2",
                name="Strategy 2",
                growth=70.0,
                profitability=85.0,
                innovation=55.0,
                stability=60.0,
            ),
            StrategyCandidate(
                id="s3",
                name="Strategy 3",
                growth=60.0,
                profitability=75.0,
                innovation=80.0,
                stability=50.0,
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
            id="insights_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

        engine = TradeoffGradientEngine()
        result = engine.compute_tradeoff_gradients(frontier)

        # Verify insights are meaningful
        for insight in result.actionable_insights:
            assert isinstance(insight, str)
            assert len(insight) > 20  # Not trivial strings
            # Should reference objectives or tradeoffs
            relevant = any(
                keyword in insight.lower()
                for keyword in [
                    "growth",
                    "profit",
                    "innovation",
                    "stability",
                    "tradeoff",
                    "gradient",
                    "sacrifice",
                ]
            )
            assert relevant
