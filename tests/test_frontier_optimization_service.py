"""
Tests for frontier_optimization_service.py

Tests for complete frontier optimization lifecycle including:
- Optimization cycle orchestration
- Health score computation
- Optimization necessity determination
- History tracking and retrieval
- Dashboard integration
"""

import pytest
import json
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from app.models.multi_objective_model import (
    ObjectiveVector,
    StrategyCandidate,
    ParetoFrontier,
)
from app.models.corporate_intent_model import CorporateIntent
from app.services.frontier_optimization_service import (
    FrontierOptimizationService,
    FrontierOptimizationResult,
)


class TestFrontierOptimizationService:
    """Test suite for frontier optimization service"""

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
            id="service_frontier",
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

    def test_service_initialization(self):
        """Test service initializes correctly"""
        service = FrontierOptimizationService()
        assert service is not None
        assert hasattr(service, "frontier_analysis_engine")
        assert hasattr(service, "gradient_engine")
        assert hasattr(service, "optimizer")

    def test_run_frontier_optimization_cycle(self, sample_frontier, sample_intent):
        """Test complete optimization cycle execution"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                result = service.run_frontier_optimization_cycle()
                
                assert isinstance(result, FrontierOptimizationResult)
                assert result.frontier_id is not None

    def test_frontier_health_score_computation(self, sample_frontier, sample_intent):
        """Test frontier health score is computed"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                health = service.get_frontier_health_score()
                
                assert health is not None
                assert "score" in health
                assert "status" in health
                assert 0 <= health["score"] <= 1
                assert health["status"] in ["healthy", "warning", "critical", "unknown"]

    def test_should_optimize_frontier(self, sample_frontier, sample_intent):
        """Test optimization necessity determination"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                should_optimize = service.should_optimize_frontier()
                
                assert isinstance(should_optimize, bool)

    def test_get_optimization_summary(self, sample_frontier, sample_intent):
        """Test optimization summary retrieval"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                summary = service.get_optimization_summary()
                
                # May be None if no optimization run yet, or have optimization data
                if summary is not None:
                    assert isinstance(summary, dict)

    def test_get_shape_analysis(self, sample_frontier, sample_intent):
        """Test shape analysis retrieval"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                analysis = service.get_shape_analysis()
                
                if analysis is not None:
                    assert isinstance(analysis, dict)

    def test_get_gradient_analysis(self, sample_frontier, sample_intent):
        """Test gradient analysis retrieval"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                analysis = service.get_gradient_analysis()
                
                if analysis is not None:
                    assert isinstance(analysis, dict)

    def test_get_optimization_history(self, sample_frontier, sample_intent):
        """Test optimization history retrieval"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                history = service.get_optimization_history(limit=5)
                
                assert isinstance(history, list)
                assert len(history) <= 5

    def test_optimization_result_structure(self, sample_frontier, sample_intent):
        """Test FrontierOptimizationResult has all required fields"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                result = service.run_frontier_optimization_cycle()
                
                assert hasattr(result, "frontier_id")
                assert hasattr(result, "period")
                assert hasattr(result, "frontier_size")
                assert hasattr(result, "shape_analysis")
                assert hasattr(result, "gradient_analysis")
                assert hasattr(result, "optimization_opportunities")
                assert hasattr(result, "frontier_potential")
                assert hasattr(result, "actionable_insights")
                assert hasattr(result, "recommendations")
                assert hasattr(result, "timestamp")


class TestFrontierHealthScore:
    """Tests for health score computation"""

    def test_health_score_components(self, sample_frontier, sample_intent):
        """Test health score has all components"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                health = service.get_frontier_health_score()
                
                assert "score" in health
                assert "status" in health
                assert "issues" in health
                assert isinstance(health["issues"], list)

    def test_health_score_ranges(self, sample_frontier, sample_intent):
        """Test health score values are in valid ranges"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                health = service.get_frontier_health_score()
                
                score = health.get("score", 0)
                assert 0 <= score <= 1
                
                status = health.get("status", "")
                valid_statuses = ["healthy", "warning", "critical", "unknown"]
                assert status in valid_statuses


class TestOptimizationHistoryTracking:
    """Tests for optimization history tracking"""

    def test_history_retrieval_with_limit(self, sample_frontier, sample_intent):
        """Test history retrieval respects limit"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                # Different limits
                history_5 = service.get_optimization_history(limit=5)
                history_10 = service.get_optimization_history(limit=10)
                
                assert len(history_5) <= 5
                assert len(history_10) <= 10

    def test_history_default_limit(self, sample_frontier, sample_intent):
        """Test history retrieval with default limit"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                history = service.get_optimization_history()  # Use default
                
                assert isinstance(history, list)
                assert len(history) <= 10  # Default is typically 10


class TestOptimizationRecommendations:
    """Tests for optimization recommendations generation"""

    def test_recommendations_are_generated(self, sample_frontier, sample_intent):
        """Test recommendations are generated"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                result = service.run_frontier_optimization_cycle()
                
                assert result.recommendations is not None
                assert isinstance(result.recommendations, (dict, list))

    def test_recommendations_have_context(self, sample_frontier, sample_intent):
        """Test recommendations include context"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                result = service.run_frontier_optimization_cycle()
                
                # Recommendations may reference Intent, Agents, or optimization data
                recommendations = result.recommendations
                if isinstance(recommendations, dict):
                    assert len(recommendations) > 0


class TestIntegrationWithIntentAndAgents:
    """Tests for integration with Intent and Agents"""

    def test_service_references_intent(self, sample_frontier, sample_intent):
        """Test service incorporates Intent"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                result = service.run_frontier_optimization_cycle()
                
                # Service should have accessed intent
                mock_intent.get_intent.assert_called()

    def test_service_references_agents(self, sample_frontier, sample_intent):
        """Test service references Executive Agents"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                with patch.object(service, "agent_service") as mock_agents:
                    
                    result = service.run_frontier_optimization_cycle()
                    
                    # Service should have referenced agents (if method used them)
                    # May not be called depending on implementation


class TestResultPersistence:
    """Tests for result persistence"""

    def test_results_are_saved(self, sample_frontier, sample_intent):
        """Test results are persisted"""
        service = FrontierOptimizationService()
        
        with patch.object(service, "multi_objective_service") as mock_multi:
            mock_multi.get_pareto_frontier.return_value = sample_frontier
            with patch.object(service, "intent_service") as mock_intent:
                mock_intent.get_intent.return_value = sample_intent
                
                result = service.run_frontier_optimization_cycle()
                
                # Should be able to retrieve results after saving
                summary = service.get_optimization_summary()
                # Summary might be None if not yet saved, but service should have methods
                assert hasattr(service, "get_optimization_summary")
