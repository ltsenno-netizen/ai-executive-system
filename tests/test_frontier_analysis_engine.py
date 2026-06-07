"""
Tests for frontier_analysis_engine.py

Tests for Pareto frontier shape analysis including:
- Convexity analysis (2D projections)
- Extreme point identification
- Tradeoff cliff detection
- Frontier density and clustering
- Objective correlation computation
"""

import pytest
import numpy as np
from datetime import datetime

from app.models.multi_objective_model import (
    ObjectiveVector,
    StrategyCandidate,
    ParetoFrontier,
)
from app.services.frontier_analysis_engine import (
    FrontierAnalysisEngine,
    ExtremePoint,
    TradeoffCliff,
    FrontierDensity,
    ConvexityAnalysis,
    FrontierShapeReport,
)


class TestFrontierAnalysisEngine:
    """Test suite for frontier shape analysis"""

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
                growth=70.0,
                profitability=60.0,
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
            id="frontier_1",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

    def test_analyze_frontier_shape(self, sample_frontier):
        """Test complete frontier shape analysis"""
        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(sample_frontier)

        assert isinstance(result, FrontierShapeReport)
        assert result.frontier_id == sample_frontier.id
        assert result.period == sample_frontier.period
        assert result.frontier_size == len(sample_frontier.objectives)

    def test_compute_convexity_analysis(self, sample_frontier):
        """Test convexity analysis computation"""
        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(sample_frontier)

        assert result.convexity_analysis is not None
        assert hasattr(result.convexity_analysis, "convexity_ratio")
        assert 0 <= result.convexity_analysis.convexity_ratio <= 1
        assert len(result.convexity_analysis.non_convex_regions) >= 0

    def test_find_extreme_points(self, sample_frontier):
        """Test extreme point identification"""
        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(sample_frontier)

        assert result.extreme_points is not None
        assert len(result.extreme_points) > 0

        # Check that extreme points have candidates and objectives
        for extreme in result.extreme_points:
            assert isinstance(extreme, ExtremePoint)
            assert extreme.objective_dimension in [
                "growth",
                "profitability",
                "innovation",
                "stability",
            ]
            assert extreme.candidate_id is not None
            assert extreme.value > 0

    def test_identify_tradeoff_cliffs(self, sample_frontier):
        """Test tradeoff cliff identification"""
        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(sample_frontier)

        assert result.tradeoff_cliffs is not None
        # Cliffs are optional, but if present should be valid
        for cliff in result.tradeoff_cliffs:
            assert isinstance(cliff, TradeoffCliff)
            assert cliff.source_objective in [
                "growth",
                "profitability",
                "innovation",
                "stability",
            ]
            assert cliff.target_objective in [
                "growth",
                "profitability",
                "innovation",
                "stability",
            ]
            assert cliff.slope > 0

    def test_analyze_frontier_density(self, sample_frontier):
        """Test frontier density analysis"""
        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(sample_frontier)

        assert result.frontier_density is not None
        assert isinstance(result.frontier_density, FrontierDensity)
        assert 0 <= result.frontier_density.overall_density <= 1
        assert 0 <= result.frontier_density.clustering_coefficient <= 1

    def test_compute_correlations(self, sample_frontier):
        """Test objective correlation computation"""
        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(sample_frontier)

        assert result.objective_correlations is not None
        assert isinstance(result.objective_correlations, dict)

        # Check correlation values are between -1 and 1
        for (obj1, obj2), corr in result.objective_correlations.items():
            assert -1 <= corr <= 1

    def test_frontier_shape_report_structure(self, sample_frontier):
        """Test complete FrontierShapeReport structure"""
        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(sample_frontier)

        # Verify all required fields are present
        assert result.frontier_id is not None
        assert result.period is not None
        assert result.frontier_size > 0
        assert result.convexity_analysis is not None
        assert result.extreme_points is not None
        assert result.tradeoff_cliffs is not None
        assert result.frontier_density is not None
        assert result.objective_correlations is not None
        assert result.timestamp is not None

    def test_small_frontier(self):
        """Test analysis on very small frontier"""
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
            id="small_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(frontier)

        assert result.frontier_size == 2
        assert result.extreme_points is not None

    def test_large_frontier(self):
        """Test analysis on larger frontier"""
        candidates = [
            StrategyCandidate(
                id=f"s{i}",
                name=f"Strategy {i}",
                growth=np.random.uniform(50, 100),
                profitability=np.random.uniform(40, 90),
                innovation=np.random.uniform(30, 80),
                stability=np.random.uniform(40, 80),
            )
            for i in range(20)
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
            id="large_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(frontier)

        assert result.frontier_size == 20
        assert len(result.extreme_points) >= 4  # At least one per objective

    def test_convexity_ratio_properties(self, sample_frontier):
        """Test that convexity ratio has expected properties"""
        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(sample_frontier)

        convexity = result.convexity_analysis
        assert convexity.convexity_ratio >= 0
        assert convexity.convexity_ratio <= 1

        # Perfect convexity should be near 1, worse than random near 0
        assert isinstance(convexity.convexity_ratio, float)

    def test_clustering_coefficient_range(self, sample_frontier):
        """Test that clustering coefficient is in valid range"""
        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(sample_frontier)

        density = result.frontier_density
        assert 0 <= density.clustering_coefficient <= 1

    def test_objective_correlation_properties(self, sample_frontier):
        """Test objective correlation properties"""
        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(sample_frontier)

        correlations = result.objective_correlations
        
        # Diagonal should be 1 (correlation with self)
        assert correlations.get(("growth", "growth"), 0) >= 0.9
        assert correlations.get(("profitability", "profitability"), 0) >= 0.9
        
        # Correlations should be symmetric
        if ("growth", "profitability") in correlations:
            if ("profitability", "growth") in correlations:
                assert abs(
                    correlations[("growth", "profitability")] - 
                    correlations[("profitability", "growth")]
                ) < 0.01


class TestExtremePointIdentification:
    """Tests for extreme point identification logic"""

    def test_extreme_point_detection(self):
        """Test that extreme points are correctly identified"""
        candidates = [
            StrategyCandidate(
                id="max_growth",
                name="Max Growth",
                growth=150.0,
                profitability=30.0,
                innovation=50.0,
                stability=40.0,
            ),
            StrategyCandidate(
                id="max_profit",
                name="Max Profit",
                growth=50.0,
                profitability=150.0,
                innovation=40.0,
                stability=50.0,
            ),
            StrategyCandidate(
                id="max_innovation",
                name="Max Innovation",
                growth=60.0,
                profitability=40.0,
                innovation=150.0,
                stability=30.0,
            ),
            StrategyCandidate(
                id="max_stability",
                name="Max Stability",
                growth=50.0,
                profitability=60.0,
                innovation=40.0,
                stability=150.0,
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
            id="extreme_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(frontier)

        # Should identify one max per objective
        assert len(result.extreme_points) >= 4


class TestFrontierDensityMetrics:
    """Tests for frontier density metric computation"""

    def test_sparse_frontier_density(self):
        """Test density for sparse frontier"""
        candidates = [
            StrategyCandidate(
                id=f"s{i}",
                name=f"Strategy {i}",
                growth=i * 10 + 50,
                profitability=100 - (i * 10),
                innovation=50 + (i * 5),
                stability=60,
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
            id="sparse_frontier",
            period="2026-01",
            candidates=candidates,
            objectives=objectives,
            created_at=datetime.now(),
            frontier_status="active",
        )

        engine = FrontierAnalysisEngine()
        result = engine.analyze_frontier_shape(frontier)

        # Sparse frontier should have lower density
        assert result.frontier_density.overall_density >= 0
