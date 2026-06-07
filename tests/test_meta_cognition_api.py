"""
Tests for the Meta-Cognition API routes.
"""

import pytest
import shutil
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from src.backend.app.main import app
from src.backend.app.routes import meta_cognition as meta_cognition_route
from src.backend.app.services.meta_cognition_service import MetaCognitionService
from src.backend.app.services.corporate_memory_service import CorporateMemoryService


@pytest.fixture
def client():
    meta_cognition_route._service = None
    return TestClient(app)


@pytest.fixture
def temp_data_dir(monkeypatch):
    temp_dir = Path(tempfile.mkdtemp())
    meta_dir = temp_dir / "meta_cognition"
    memory_dir = temp_dir / "corporate_memory"
    meta_dir.mkdir(parents=True)
    memory_dir.mkdir(parents=True)

    monkeypatch.setattr(MetaCognitionService, "DATA_DIR", meta_dir)
    monkeypatch.setattr(MetaCognitionService, "REPORTS_FILE", meta_dir / "reports.json")
    monkeypatch.setattr(CorporateMemoryService, "MEMORY_DIR", memory_dir)
    monkeypatch.setattr(CorporateMemoryService, "MEMORY_FILE", memory_dir / "memory.json")

    meta_cognition_route._service = None
    yield temp_dir

    shutil.rmtree(temp_dir)
    meta_cognition_route._service = None


def test_run_meta_cognition_assessment(client, temp_data_dir):
    response = client.post("/api/meta-cognition/run")
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert "overall_score" in data
    assert len(data["scores"]) == 8


def test_get_latest_meta_cognition_report(client, temp_data_dir):
    client.post("/api/meta-cognition/run")
    response = client.get("/api/meta-cognition/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["report_id"]


def test_get_meta_cognition_history(client, temp_data_dir):
    client.post("/api/meta-cognition/run")
    response = client.get("/api/meta-cognition/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_meta_cognition_markdown(client, temp_data_dir):
    run_response = client.post("/api/meta-cognition/run")
    report_id = run_response.json()["report_id"]

    response = client.get(f"/api/meta-cognition/markdown/{report_id}")
    assert response.status_code == 200
    data = response.json()
    assert "markdown" in data
    assert report_id in data["markdown"]


def test_get_meta_cognition_markdown_not_found(client, temp_data_dir):
    response = client.get("/api/meta-cognition/markdown/invalid-id")
    assert response.status_code == 404
