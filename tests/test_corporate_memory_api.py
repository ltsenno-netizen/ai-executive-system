"""
Tests for Corporate Memory API Routes
=====================================
"""

import pytest
from fastapi.testclient import TestClient
import tempfile
import shutil
from pathlib import Path

from src.backend.app.main import app
from src.backend.app.services.corporate_memory_service import CorporateMemoryService
from src.backend.app.models.corporate_memory_model import MemoryItemType, MemoryImportance


@pytest.fixture
def client():
    """Create a test client for the API."""
    import src.backend.app.routes.corporate_memory as corporate_memory_route
    corporate_memory_route._service = None
    return TestClient(app)


@pytest.fixture
def temp_data_dir(monkeypatch):
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    memory_dir = Path(temp_dir) / "corporate_memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    # Patch the service to use temp directory
    original_memory_dir = CorporateMemoryService.MEMORY_DIR
    original_memory_file = CorporateMemoryService.MEMORY_FILE
    
    CorporateMemoryService.MEMORY_DIR = memory_dir
    CorporateMemoryService.MEMORY_FILE = memory_dir / "memory.json"
    
    # Reset any cached service instance in the API router
    import src.backend.app.routes.corporate_memory as corporate_memory_route
    corporate_memory_route._service = None
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)
    CorporateMemoryService.MEMORY_DIR = original_memory_dir
    CorporateMemoryService.MEMORY_FILE = original_memory_file
    corporate_memory_route._service = None


class TestAddMemoryEndpoint:
    """Tests for POST /memory/add endpoint."""
    
    def test_add_memory_success(self, client, temp_data_dir):
        """Test successfully adding a memory."""
        response = client.post(
            "/api/memory/add",
            json={
                "item_type": "decision",
                "title": "Budget Allocation",
                "description": "Approved Q4 budget allocation",
                "context": {"total_budget": 1000000},
                "importance": "high",
                "tags": ["budget", "quarterly"],
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Budget Allocation"
        assert data["item_type"] == "DECISION"
        assert data["importance"] == "HIGH"

    def test_add_memory_invalid_type(self, client, temp_data_dir):
        """Test adding memory with invalid type."""
        response = client.post(
            "/api/memory/add",
            json={
                "item_type": "invalid_type",
                "title": "Test",
                "description": "Test",
                "context": {},
            }
        )
        
        assert response.status_code == 400

    def test_add_memory_invalid_importance(self, client, temp_data_dir):
        """Test adding memory with invalid importance."""
        response = client.post(
            "/api/memory/add",
            json={
                "item_type": "decision",
                "title": "Test",
                "description": "Test",
                "context": {},
                "importance": "invalid_importance",
            }
        )
        
        assert response.status_code == 400


class TestGetMemoriesEndpoint:
    """Tests for GET /memory/all endpoint."""
    
    def setup_method(self):
        """Setup test data."""
        self.temp_dir = tempfile.mkdtemp()
        memory_dir = Path(self.temp_dir) / "corporate_memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.original_memory_dir = CorporateMemoryService.MEMORY_DIR
        self.original_memory_file = CorporateMemoryService.MEMORY_FILE
        CorporateMemoryService.MEMORY_DIR = memory_dir
        CorporateMemoryService.MEMORY_FILE = memory_dir / "memory.json"

    def teardown_method(self):
        """Cleanup."""
        shutil.rmtree(self.temp_dir)
        CorporateMemoryService.MEMORY_DIR = self.original_memory_dir
        CorporateMemoryService.MEMORY_FILE = self.original_memory_file

    def test_get_all_memories(self, client):
        """Test getting all memories."""
        # Add some test memories
        for i in range(3):
            client.post(
                "/api/memory/add",
                json={
                    "item_type": "decision",
                    "title": f"Decision {i}",
                    "description": f"Description {i}",
                    "context": {},
                }
            )
        
        response = client.get("/api/memory/all")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_memories_with_limit(self, client):
        """Test getting memories with limit."""
        # Add 10 memories
        for i in range(10):
            client.post(
                "/api/memory/add",
                json={
                    "item_type": "decision",
                    "title": f"Memory {i}",
                    "description": f"Desc {i}",
                    "context": {},
                }
            )
        
        response = client.get("/api/memory/all?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5


class TestGetMemoryByIdEndpoint:
    """Tests for GET /memory/{id} endpoint."""
    
    def test_get_existing_memory(self, client, temp_data_dir):
        """Test getting an existing memory."""
        # Add a memory
        add_response = client.post(
            "/api/memory/add",
            json={
                "item_type": "decision",
                "title": "Test Decision",
                "description": "For retrieval test",
                "context": {"test": True},
            }
        )
        memory_id = add_response.json()["memory_id"]
        
        # Get the memory
        get_response = client.get(f"/api/memory/{memory_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["title"] == "Test Decision"
        assert data["memory_id"] == memory_id

    def test_get_nonexistent_memory(self, client, temp_data_dir):
        """Test getting a non-existent memory."""
        response = client.get("/api/memory/nonexistent_id_12345")
        assert response.status_code == 404


class TestGetMemoriesByTypeEndpoint:
    """Tests for GET /memory/type/{type} endpoint."""
    
    def test_get_memories_by_type(self, client, temp_data_dir):
        """Test getting memories by type."""
        # Add memories of different types
        for i in range(3):
            client.post(
                "/api/memory/add",
                json={
                    "item_type": "decision",
                    "title": f"Decision {i}",
                    "description": f"Desc {i}",
                    "context": {},
                }
            )
        
        for i in range(2):
            client.post(
                "/api/memory/add",
                json={
                    "item_type": "intent_change",
                    "title": f"Intent Change {i}",
                    "description": f"Desc {i}",
                    "context": {},
                }
            )
        
        # Get only decisions
        response = client.get("/api/memory/type/decision")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(m["item_type"] == "DECISION" for m in data)

    def test_get_memories_by_type_invalid(self, client, temp_data_dir):
        """Test getting memories by invalid type."""
        response = client.get("/api/memory/type/invalid_type")
        assert response.status_code == 400


class TestQueryMemoriesEndpoint:
    """Tests for POST /memory/query endpoint."""
    
    def test_query_memories(self, client, temp_data_dir):
        """Test querying memories with filters."""
        # Add test memories
        for i in range(5):
            client.post(
                "/api/memory/add",
                json={
                    "item_type": "decision",
                    "title": f"Decision {i}",
                    "description": f"Description {i}",
                    "context": {},
                    "importance": "high" if i < 3 else "medium",
                }
            )
        
        # Query for high importance
        response = client.post(
            "/api/memory/query",
            json={
                "importance_levels": ["high"],
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 3
        assert len(data["memories"]) == 3


class TestMemorySummaryEndpoint:
    """Tests for GET /memory/summary endpoint."""
    
    def test_get_memory_summary(self, client, temp_data_dir):
        """Test getting memory summary."""
        # Add test memories
        for i in range(5):
            client.post(
                "/api/memory/add",
                json={
                    "item_type": "decision",
                    "title": f"Memory {i}",
                    "description": f"Desc {i}",
                    "context": {},
                }
            )
        
        response = client.get("/api/memory/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_memories"] == 5
        assert isinstance(data["memory_types"], dict)


class TestMemoryExportEndpoint:
    """Tests for markdown export endpoints."""
    
    def test_export_single_memory_markdown(self, client, temp_data_dir):
        """Test exporting single memory as markdown."""
        # Add a memory
        add_response = client.post(
            "/api/memory/add",
            json={
                "item_type": "decision",
                "title": "Export Test",
                "description": "For export test",
                "context": {"key": "value"},
            }
        )
        memory_id = add_response.json()["memory_id"]
        
        # Export as markdown
        response = client.get(f"/api/memory/{memory_id}/markdown")
        assert response.status_code == 200
        data = response.json()
        assert "markdown" in data
        assert "Export Test" in data["markdown"]

    def test_export_all_memories_markdown(self, client, temp_data_dir):
        """Test exporting all memories as markdown."""
        # Add test memories
        for i in range(3):
            client.post(
                "/api/memory/add",
                json={
                    "item_type": "decision",
                    "title": f"Memory {i}",
                    "description": f"Desc {i}",
                    "context": {},
                }
            )
        
        response = client.get("/api/memory/markdown/all")
        assert response.status_code == 200
        data = response.json()
        assert "markdown" in data
        assert "Corporate Memory Export" in data["markdown"]


class TestMemoryTypeAndImportanceEndpoints:
    """Tests for metadata endpoints."""
    
    def test_get_memory_types(self, client):
        """Test getting available memory types."""
        response = client.get("/api/memory/types")
        assert response.status_code == 200
        data = response.json()
        assert "types" in data
        assert "DECISION" in data["types"]
        assert "CRISIS_EVENT" in data["types"]

    def test_get_importance_levels(self, client):
        """Test getting importance levels."""
        response = client.get("/api/memory/importances")
        assert response.status_code == 200
        data = response.json()
        assert "levels" in data
        assert "CRITICAL" in data["levels"]
        assert "HIGH" in data["levels"]


class TestMemoryMetricsEndpoint:
    """Tests for metrics endpoint."""
    
    def test_get_memory_metrics(self, client, temp_data_dir):
        """Test getting memory metrics."""
        # Add some test memories
        for i in range(5):
            client.post(
                "/api/memory/add",
                json={
                    "item_type": "decision",
                    "title": f"Memory {i}",
                    "description": f"Desc {i}",
                    "context": {},
                }
            )
        
        response = client.get("/api/memory/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_memories"] == 5
        assert isinstance(data["memory_types"], dict)
        assert isinstance(data["importance_distribution"], dict)


class TestSpecializedEndpoints:
    """Tests for specialized memory retrieval endpoints."""
    
    def test_get_intent_changes(self, client, temp_data_dir):
        """Test getting intent change memories."""
        # Add intent changes
        for i in range(3):
            client.post(
                "/api/memory/add",
                json={
                    "item_type": "intent_change",
                    "title": f"Intent Change {i}",
                    "description": f"Desc {i}",
                    "context": {},
                }
            )
        
        response = client.get("/api/memory/intent-changes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_decisions(self, client, temp_data_dir):
        """Test getting decision memories."""
        # Add decisions
        for i in range(3):
            client.post(
                "/api/memory/add",
                json={
                    "item_type": "decision",
                    "title": f"Decision {i}",
                    "description": f"Desc {i}",
                    "context": {},
                }
            )
        
        response = client.get("/api/memory/decisions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
