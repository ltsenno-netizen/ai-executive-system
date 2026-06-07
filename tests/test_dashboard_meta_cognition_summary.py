"""
Tests for executive dashboard meta-cognition summary integration.
"""

from pathlib import Path

from src.backend.app.services.executive_dashboard_service import ExecutiveDashboardService
from src.backend.app.services.meta_cognition_service import MetaCognitionService


def test_aggregate_meta_cognition_summary(monkeypatch, tmp_path):
    reports_dir = tmp_path / "meta_cognition"
    reports_dir.mkdir()

    monkeypatch.setattr(MetaCognitionService, "DATA_DIR", reports_dir)
    monkeypatch.setattr(MetaCognitionService, "REPORTS_FILE", reports_dir / "reports.json")

    meta_service = MetaCognitionService()
    report = meta_service.run_assessment(save_to_memory=False)

    dashboard_service = ExecutiveDashboardService()
    summary = dashboard_service.aggregate_meta_cognition_summary()

    assert summary is not None
    assert summary.overall_score == report.overall_score
    assert summary.top_risks == [bias.name for bias in report.biases[:3]]
    assert summary.strongest_dimensions == [s.dimension.value for s in sorted(report.scores, key=lambda x: x.score, reverse=True)[:3]]
