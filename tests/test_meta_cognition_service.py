"""
Tests for the Meta-Cognition service layer.
"""

import shutil
from pathlib import Path
import tempfile

from src.backend.app.services.meta_cognition_service import MetaCognitionService
from src.backend.app.services.corporate_memory_service import CorporateMemoryService


def test_run_assessment_creates_report_and_history(tmp_path, monkeypatch):
    reports_dir = tmp_path / "meta_cognition"
    reports_dir.mkdir()
    memory_dir = tmp_path / "corporate_memory"
    memory_dir.mkdir()

    monkeypatch.setattr(MetaCognitionService, "DATA_DIR", reports_dir)
    monkeypatch.setattr(MetaCognitionService, "REPORTS_FILE", reports_dir / "reports.json")
    monkeypatch.setattr(CorporateMemoryService, "MEMORY_DIR", memory_dir)
    monkeypatch.setattr(CorporateMemoryService, "MEMORY_FILE", memory_dir / "memory.json")

    service = MetaCognitionService()
    report = service.run_assessment(save_to_memory=False)

    assert report.report_id
    assert len(report.scores) == 8
    assert service.get_latest().report_id == report.report_id
    assert len(service.get_history()) == 1

    markdown = service.export_report_markdown(report.report_id)
    assert markdown is not None
    assert "Meta-Cognition Report" in markdown


def test_get_latest_returns_none_when_no_reports(tmp_path, monkeypatch):
    reports_dir = tmp_path / "meta_cognition"
    reports_dir.mkdir()
    monkeypatch.setattr(MetaCognitionService, "DATA_DIR", reports_dir)
    monkeypatch.setattr(MetaCognitionService, "REPORTS_FILE", reports_dir / "reports.json")

    service = MetaCognitionService()
    assert service.get_latest() is None
    assert service.get_history() == []
