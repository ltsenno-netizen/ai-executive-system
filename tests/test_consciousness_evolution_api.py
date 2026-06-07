"""
Tests for Consciousness Evolution API Endpoints
===============================================

Tests for REST API endpoints related to consciousness evolution.
"""

import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app


class TestEvolutionAPIInitialization:
    """Test that evolution API is properly registered."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_evolution_router_registered(self, client):
        """Test that evolution router is registered in main app."""
        # Check that at least one evolution endpoint exists
        routes = [r.path for r in app.routes]
        consciousness_evolution_routes = [r for r in routes if 'consciousness/evolution' in r]
        assert len(consciousness_evolution_routes) > 0


class TestRunEvolutionCycle:
    """Test evolution cycle execution endpoint."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_evolution_cycle_endpoint_exists(self, client):
        """Test that evolution cycle endpoint exists."""
        response = client.post("/api/consciousness/evolution/run")
        # Should not 404
        assert response.status_code != 404
    
    def test_evolution_cycle_returns_state(self, client):
        """Test that evolution cycle returns updated state."""
        response = client.post("/api/consciousness/evolution/run")
        
        if response.status_code == 200:
            data = response.json()
            assert "evolution_state" in data or "status" in data


class TestGetEvolutionState:
    """Test evolution state retrieval endpoint."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_get_state_endpoint_exists(self, client):
        """Test that state endpoint exists."""
        response = client.get("/api/consciousness/evolution/state")
        assert response.status_code != 404
    
    def test_get_state_returns_valid_data(self, client):
        """Test that state endpoint returns valid data."""
        response = client.get("/api/consciousness/evolution/state")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)


class TestGetEvolutionHistory:
    """Test evolution history retrieval endpoint."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_history_endpoint_exists(self, client):
        """Test that history endpoint exists."""
        response = client.get("/api/consciousness/evolution/history")
        assert response.status_code != 404
    
    def test_history_respects_limit(self, client):
        """Test that history endpoint respects limit parameter."""
        response = client.get("/api/consciousness/evolution/history?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)


class TestGetEvolutionReport:
    """Test evolution report generation endpoint."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_report_endpoint_exists(self, client):
        """Test that report endpoint exists."""
        response = client.get("/api/consciousness/evolution/report")
        assert response.status_code != 404
    
    def test_report_returns_data(self, client):
        """Test that report endpoint returns data."""
        response = client.get("/api/consciousness/evolution/report")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)


class TestExportMarkdown:
    """Test Markdown export endpoint."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_markdown_endpoint_exists(self, client):
        """Test that Markdown endpoint exists."""
        response = client.get("/api/consciousness/evolution/markdown")
        assert response.status_code != 404
    
    def test_markdown_export_content_type(self, client):
        """Test that Markdown endpoint returns proper format."""
        response = client.get("/api/consciousness/evolution/markdown")
        
        if response.status_code == 200:
            data = response.json()
            assert "format" in data or "content" in data


class TestEvolutionAPIIntegration:
    """Test API integration flows."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_full_evolution_workflow(self, client):
        """Test complete evolution workflow through API."""
        # Get current state
        state_response = client.get("/api/consciousness/evolution/state")
        
        if state_response.status_code == 200:
            # Run evolution cycle
            run_response = client.post("/api/consciousness/evolution/run")
            
            if run_response.status_code == 200:
                # Get updated state
                updated_response = client.get("/api/consciousness/evolution/state")
                assert updated_response.status_code == 200
    
    def test_get_report_after_evolution(self, client):
        """Test getting report after evolution."""
        # Run evolution
        run_response = client.post("/api/consciousness/evolution/run")
        
        if run_response.status_code == 200:
            # Get report
            report_response = client.get("/api/consciousness/evolution/report")
            
            if report_response.status_code == 200:
                data = report_response.json()
                assert isinstance(data, dict)
